# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Async client for an HP printer's embedded web server (EWS)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp

from .const import (
    _LOGGER,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    ENDPOINT_ADAPTERS,
    ENDPOINT_CONSUMABLE_CONFIG,
    ENDPOINT_EPRINT_CONFIG,
    ENDPOINT_NET_APPS_SECURE,
    ENDPOINT_PRODUCT_CONFIG,
    ENDPOINT_PRODUCT_STATUS,
    ENDPOINT_PRODUCT_USAGE,
)
from .exceptions import (
    HpPrinterConnectionError,
    HpPrinterError,
    HpPrinterHttpError,
    HpPrinterTimeoutError,
)
from .models import HpPrinterData
from .parsers import (
    parse_adapters,
    parse_consumables,
    parse_copy_usage,
    parse_device,
    parse_eprint,
    parse_fax_usage,
    parse_printer_usage,
    parse_scanner_usage,
    parse_status,
    parse_wifi,
)
from .xml import parse_document, parse_json_document

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable
    from types import TracebackType
    from typing import Any, Self

    from .models import (
        HpAdapter,
        HpConsumable,
        HpCopyUsage,
        HpEPrint,
        HpFaxUsage,
        HpPrinterDevice,
        HpPrinterStatus,
        HpPrinterUsage,
        HpScannerUsage,
        HpWifi,
    )


class HpPrinter:
    """Async client for an HP printer's embedded web server (EWS).

    Session ownership: when no `session` is given, `HpPrinter` creates and
    owns an `aiohttp.ClientSession` for the lifetime of the `async with`
    block (or until :meth:`close` is called). When a `session` is injected
    - the recommended approach for applications such as Home Assistant that
    manage their own connection pooling - the caller owns it and remains
    responsible for closing it; `HpPrinter` never closes a session it did
    not create.
    """

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession | None = None,
        *,
        port: int = DEFAULT_PORT,
        ssl: bool = False,
        timeout: aiohttp.ClientTimeout = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client for the printer at `host`."""
        self._host = host
        self._port = port
        self._ssl = ssl
        self._timeout = timeout
        self._session = session
        self._owns_session = session is None

    @property
    def base_url(self) -> str:
        """Return the printer's EWS base URL."""
        protocol = "https" if self._ssl else "http"
        return f"{protocol}://{self._host}:{self._port}"

    async def __aenter__(self) -> Self:
        """Open the client, creating a session if none was injected."""
        if self._session is None:
            self._session = aiohttp.ClientSession()

        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the client, releasing only a session it created itself."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying session, if this client owns it."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def is_online(self) -> bool:
        """Return whether the printer currently responds to status requests.

        Any failure - offline, powered down, unreachable, or an unexpected
        response - is treated as "not online" rather than raised, since that
        is what this check exists to answer. Call :meth:`status` directly to
        distinguish those failure modes.
        """
        try:
            await self.status()
        except HpPrinterError:
            return False

        return True

    async def device(self) -> HpPrinterDevice:
        """Fetch printer identity information."""
        document = await self._request(ENDPOINT_PRODUCT_CONFIG)

        return parse_device(document)

    async def status(self) -> HpPrinterStatus:
        """Fetch the printer's current operational status."""
        document = await self._request(ENDPOINT_PRODUCT_STATUS)

        return parse_status(document)

    async def consumables(self) -> list[HpConsumable]:
        """Fetch the merged list of ink/toner consumables."""
        config_document = await self._request(ENDPOINT_CONSUMABLE_CONFIG)
        usage_document = await self._request(ENDPOINT_PRODUCT_USAGE)

        return parse_consumables(config_document, usage_document)

    async def printer_usage(
        self,
        document: dict[str, Any] | None = None,
    ) -> HpPrinterUsage:
        """Fetch cumulative printer engine page counters.

        `document` lets callers that already fetched `ProductUsageDyn` (for
        example :meth:`update`) reuse it instead of requesting it again.
        """
        if document is None:
            document = await self._request(ENDPOINT_PRODUCT_USAGE)

        return parse_printer_usage(document)

    async def scanner_usage(
        self,
        document: dict[str, Any] | None = None,
    ) -> HpScannerUsage:
        """Fetch cumulative scanner engine page counters.

        See :meth:`printer_usage` for the meaning of `document`.
        """
        if document is None:
            document = await self._request(ENDPOINT_PRODUCT_USAGE)

        return parse_scanner_usage(document)

    async def copy_usage(
        self,
        document: dict[str, Any] | None = None,
    ) -> HpCopyUsage:
        """Fetch cumulative copy application page counters.

        See :meth:`printer_usage` for the meaning of `document`.
        """
        if document is None:
            document = await self._request(ENDPOINT_PRODUCT_USAGE)

        return parse_copy_usage(document)

    async def fax_usage(
        self,
        document: dict[str, Any] | None = None,
    ) -> HpFaxUsage:
        """Fetch cumulative fax application page counters.

        See :meth:`printer_usage` for the meaning of `document`.
        """
        if document is None:
            document = await self._request(ENDPOINT_PRODUCT_USAGE)

        return parse_fax_usage(document)

    async def adapters(self) -> list[HpAdapter]:
        """Fetch the printer's network adapters."""
        document = await self._request(ENDPOINT_ADAPTERS)

        return parse_adapters(document)

    async def eprint(self) -> HpEPrint:
        """Fetch HP ePrint cloud printing configuration."""
        document = await self._request(ENDPOINT_EPRINT_CONFIG)

        return parse_eprint(document)

    async def wifi(self) -> HpWifi:
        """Fetch Wireless Direct configuration."""
        document = await self._request(ENDPOINT_NET_APPS_SECURE)

        return parse_wifi(document)

    async def update(self) -> HpPrinterData:
        """Fetch everything the printer currently supports.

        Only the status endpoint is treated as required: if the printer
        does not answer it, `update` returns immediately with
        `online=False` and every other field left at its default. Every
        other endpoint is optional - a missing or failing one leaves its
        field `None` (or an empty list) without aborting the rest of the
        update, since printer models differ in which features they expose.
        """
        try:
            status = await self.status()
        except HpPrinterError:
            return HpPrinterData(online=False)

        usage_document = await self._safe_request(ENDPOINT_PRODUCT_USAGE)
        config_document = await self._safe_request(ENDPOINT_CONSUMABLE_CONFIG)

        return HpPrinterData(
            online=True,
            device=await self._safe(self.device),
            status=status,
            consumables=parse_consumables(config_document, usage_document),
            printer_usage=(
                parse_printer_usage(usage_document)
                if usage_document is not None
                else None
            ),
            scanner_usage=(
                parse_scanner_usage(usage_document)
                if usage_document is not None
                else None
            ),
            copy_usage=(
                parse_copy_usage(usage_document) if usage_document is not None else None
            ),
            fax_usage=(
                parse_fax_usage(usage_document) if usage_document is not None else None
            ),
            adapters=await self._safe(self.adapters) or [],
            eprint=await self._safe(self.eprint),
            wifi=await self._safe(self.wifi),
        )

    async def _safe[T](self, func: Callable[[], Awaitable[T]]) -> T | None:
        """Await `func`, turning any `HpPrinterError` into `None`."""
        try:
            return await func()
        except HpPrinterError:
            _LOGGER.debug("Optional endpoint unavailable for %s", func.__name__)
            return None

    async def _safe_request(self, endpoint: str) -> dict[str, Any] | None:
        """Fetch and parse `endpoint`, turning any `HpPrinterError` into `None`."""
        try:
            return await self._request(endpoint)
        except HpPrinterError:
            _LOGGER.debug("Optional endpoint unavailable: %s", endpoint)
            return None

    async def _request(self, endpoint: str) -> dict[str, Any]:
        """Fetch `endpoint` and parse it into a nested dict document."""
        if self._session is None:
            message = (
                "HpPrinter has no active session; "
                "use it as an async context manager or inject one"
            )
            raise HpPrinterConnectionError(message)

        url = f"{self.base_url}{endpoint}"

        try:
            async with self._session.get(url, timeout=self._timeout) as response:
                if response.status >= 400:  # noqa: PLR2004
                    message = f"{url} returned HTTP {response.status}"
                    raise HpPrinterHttpError(response.status, message)

                content = await response.text()
                content_type = response.content_type
        except TimeoutError as ex:
            message = f"Timed out requesting {url}"
            raise HpPrinterTimeoutError(message) from ex
        except aiohttp.ClientError as ex:
            message = f"Could not connect to {url}: {ex}"
            raise HpPrinterConnectionError(message) from ex

        if content_type == "application/javascript":
            return parse_json_document(content)

        return parse_document(content)
