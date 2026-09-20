# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Support for HP printers."""

from dataclasses import dataclass, field
from typing import Any

from aiohttp import ClientSession

from .const import _LOGGER, DEFAULT_PORT, DEFAULT_TIMEOUT


@dataclass
class HpPrinterDevice:
    """Representation of an HP printer."""

    device_id: str
    name: str
    model: str
    data: dict[str, Any] = field(default_factory=dict)


class HpPrinterApi:
    """Client for an HP printer's embedded web server (EWS)."""

    def __init__(
        self,
        host: str,
        session: ClientSession,
        *,
        port: int = DEFAULT_PORT,
        ssl: bool = False,
    ) -> None:
        """Initialize the API client."""
        self.host = host
        self.port = port
        self.ssl = ssl
        self.session = session
        self.timeout = DEFAULT_TIMEOUT

    async def get_status(self) -> HpPrinterDevice:
        """Fetch the printer's current status."""
        _LOGGER.debug("Fetching status from %s", self.host)
        raise NotImplementedError

    async def close(self) -> None:
        """Release any resources held by the client."""
