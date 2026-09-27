# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for `HpPrinter`: HTTP handling, session ownership, and `update()`.

HTTP responses are served by a real local server (`make_server`, see
`conftest.py`) rather than a transport-level mock, so these tests exercise
the client's actual request/response handling end to end: HTTP response ->
client -> parser -> model.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from aiohttp import ClientTimeout

from aiohpprinter.client import HpPrinter
from aiohpprinter.exceptions import (
    HpPrinterConnectionError,
    HpPrinterHttpError,
    HpPrinterParseError,
    HpPrinterTimeoutError,
)
from aiohpprinter.models import HpAdapter, HpPrinterData
from aiohpprinter.xml import parse_document
from tests.conftest import (
    RouteResponse,
    discover_fixtures,
    fixture_routes,
    load_expected,
    load_xml,
    to_json_safe,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiohttp import ClientSession
    from aiohttp.test_utils import TestServer

    MakeServer = Callable[[dict[str, RouteResponse]], Awaitable[TestServer]]

FULL_FIXTURE = Path(__file__).parent / "fixtures" / "hp_officejet_pro_9022e"

#: The endpoints every model answers; the rest are optional.
REQUIRED_ENDPOINTS = ("/DevMgmt/ProductStatusDyn.xml", "/DevMgmt/ProductConfigDyn.xml")

#: `update()` needs the status endpoint to report the printer online; every
#: captured fixture has it, partial ones like a lone `ProductUsageDyn.xml`
#: are only covered by the parser suite.
UPDATE_FIXTURE_DIRS = [
    fixture_dir
    for fixture_dir in discover_fixtures()
    if (fixture_dir / "ProductStatusDyn.xml").exists()
]


def _printer(
    server: TestServer,
    session: ClientSession,
    *,
    timeout: ClientTimeout | None = None,
) -> HpPrinter:
    """Build an `HpPrinter` pointed at a `make_server` instance."""
    assert server.port is not None

    if timeout is not None:
        return HpPrinter(
            server.host, session=session, port=server.port, timeout=timeout
        )

    return HpPrinter(server.host, session=session, port=server.port)


async def test_device_success(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """`device()` fetches and parses `ProductConfigDyn.xml`."""
    xml = load_xml(FULL_FIXTURE, "ProductConfigDyn.xml")
    assert xml is not None
    server = await make_server(
        {"/DevMgmt/ProductConfigDyn.xml": RouteResponse(body=xml)}
    )

    async with _printer(server, mock_session) as printer:
        device = await printer.device()

    assert to_json_safe(device) == load_expected(FULL_FIXTURE)["device"]


async def test_consumables_success(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """`consumables()` merges the config and usage endpoints."""
    config_xml = load_xml(FULL_FIXTURE, "ConsumableConfigDyn.xml")
    usage_xml = load_xml(FULL_FIXTURE, "ProductUsageDyn.xml")
    assert config_xml is not None
    assert usage_xml is not None
    server = await make_server(
        {
            "/DevMgmt/ConsumableConfigDyn.xml": RouteResponse(body=config_xml),
            "/DevMgmt/ProductUsageDyn.xml": RouteResponse(body=usage_xml),
        }
    )

    async with _printer(server, mock_session) as printer:
        consumables = await printer.consumables()

    assert to_json_safe(consumables) == load_expected(FULL_FIXTURE)["consumables"]


async def test_printer_usage_reuses_supplied_document(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """Passing a pre-fetched document skips the HTTP request entirely."""
    usage_xml = load_xml(FULL_FIXTURE, "ProductUsageDyn.xml")
    assert usage_xml is not None
    document = parse_document(usage_xml)
    # No routes registered: any request attempt would fail to connect.
    server = await make_server({})

    async with _printer(server, mock_session) as printer:
        usage = await printer.printer_usage(document)

    assert to_json_safe(usage) == load_expected(FULL_FIXTURE)["printer_usage"]


@pytest.mark.parametrize(
    "method_name",
    ["printer_usage", "scanner_usage", "copy_usage", "fax_usage"],
)
async def test_usage_methods_fetch_live_when_no_document_given(
    mock_session: ClientSession, make_server: MakeServer, method_name: str
) -> None:
    """Each usage accessor fetches `ProductUsageDyn.xml` itself by default."""
    usage_xml = load_xml(FULL_FIXTURE, "ProductUsageDyn.xml")
    assert usage_xml is not None
    server = await make_server(
        {"/DevMgmt/ProductUsageDyn.xml": RouteResponse(body=usage_xml)}
    )

    async with _printer(server, mock_session) as printer:
        method: Callable[[], Awaitable[object]] = getattr(printer, method_name)
        result = await method()

    assert to_json_safe(result) == load_expected(FULL_FIXTURE)[method_name]


@pytest.mark.parametrize("content_type", ["application/javascript", "application/json"])
async def test_adapters_via_json_content_type(
    mock_session: ClientSession, make_server: MakeServer, content_type: str
) -> None:
    """`/IoMgmt/Adapters` may reply as JSON instead of XML on some models."""
    payload = (
        '{"Adapters": {"Adapter": [{"HardwareConfig": '
        '{"Name": "Wifi1", "DeviceConnectivityPortType": "EmbeddedWifi", '
        '"IsConnected": "true"}}]}}'
    )
    server = await make_server(
        {"/IoMgmt/Adapters": RouteResponse(body=payload, content_type=content_type)}
    )

    async with _printer(server, mock_session) as printer:
        adapters = await printer.adapters()

    assert adapters == [
        HpAdapter(
            name="Wifi1", connectivity_port_type="EmbeddedWifi", is_connected=True
        )
    ]


async def test_request_raises_http_error_on_4xx(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A 4xx response raises `HpPrinterHttpError` with the status attached."""
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(status=404)}
    )

    async with _printer(server, mock_session) as printer:
        with pytest.raises(HpPrinterHttpError) as excinfo:
            await printer.status()

    assert excinfo.value.status == 404  # noqa: PLR2004


async def test_request_raises_connection_error(mock_session: ClientSession) -> None:
    """A refused connection raises `HpPrinterConnectionError`."""
    # Nothing listens on this loopback port.
    async with HpPrinter("127.0.0.1", session=mock_session, port=1) as printer:
        with pytest.raises(HpPrinterConnectionError):
            await printer.status()


async def test_request_raises_timeout_error(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A request slower than the client timeout raises `HpPrinterTimeoutError`."""
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(delay=0.2)}
    )

    async with _printer(
        server, mock_session, timeout=ClientTimeout(total=0.01)
    ) as printer:
        with pytest.raises(HpPrinterTimeoutError):
            await printer.status()


async def test_request_raises_parse_error_on_malformed_body(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A 200 response with invalid XML raises `HpPrinterParseError`."""
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(body="<not><valid")}
    )

    async with _printer(server, mock_session) as printer:
        with pytest.raises(HpPrinterParseError):
            await printer.status()


async def test_request_raises_parse_error_on_undecodable_body(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A body that cannot be decoded as its declared charset raises a parse error."""
    server = await make_server(
        {
            "/DevMgmt/ProductStatusDyn.xml": RouteResponse(
                raw_body=b"\xff\xfe not valid utf-8"
            )
        }
    )

    async with _printer(server, mock_session) as printer:
        with pytest.raises(HpPrinterParseError):
            await printer.status()


async def test_request_without_a_session_raises() -> None:
    """Using the client outside `async with` and without an injected session fails."""
    printer = HpPrinter("printer.local")

    with pytest.raises(HpPrinterConnectionError):
        await printer.status()


async def test_context_manager_owns_and_closes_its_own_session(
    make_server: MakeServer,
) -> None:
    """A client that creates its own session closes it on exit."""
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(status=404)}
    )
    assert server.port is not None

    async with HpPrinter(server.host, port=server.port) as printer:
        assert await printer.is_online() is False
        session = printer._session  # noqa: SLF001

    assert session is not None
    assert session.closed is True


async def test_context_manager_never_closes_an_injected_session(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A client using an injected session leaves it open on exit."""
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(status=404)}
    )

    async with _printer(server, mock_session) as printer:
        await printer.is_online()

    assert mock_session.closed is False


async def test_is_online_true_on_success(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """`is_online()` is `True` when the status endpoint answers normally."""
    xml = load_xml(FULL_FIXTURE, "ProductStatusDyn.xml")
    assert xml is not None
    server = await make_server(
        {"/DevMgmt/ProductStatusDyn.xml": RouteResponse(body=xml)}
    )

    async with _printer(server, mock_session) as printer:
        assert await printer.is_online() is True


async def test_is_online_false_on_any_failure(mock_session: ClientSession) -> None:
    """`is_online()` collapses every failure mode to `False`, never raising."""
    async with HpPrinter("127.0.0.1", session=mock_session, port=1) as printer:
        assert await printer.is_online() is False


async def test_update_returns_offline_without_populating_other_sections(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """When the printer is offline, `update()` returns immediately.

    Every other endpoint here would answer successfully if requested (they
    are registered with real data), so getting `online=False` back proves
    `update()` short-circuits on the status check rather than reaching them.
    """
    server = await make_server(
        fixture_routes(FULL_FIXTURE)
        | {
            "/DevMgmt/ProductStatusDyn.xml": RouteResponse(status=404),
        }
    )

    async with _printer(server, mock_session) as printer:
        data = await printer.update()

    assert data == HpPrinterData(online=False)


@pytest.mark.parametrize("fixture_dir", UPDATE_FIXTURE_DIRS, ids=lambda p: p.name)
async def test_update_fixture(
    mock_session: ClientSession, make_server: MakeServer, fixture_dir: Path
) -> None:
    """`update()` against a fixture's endpoints matches its `expected.json`.

    Endpoints the fixture has no file for answer 404, as they would on a
    model that lacks them.
    """
    server = await make_server(fixture_routes(fixture_dir, missing_status=404))

    async with _printer(server, mock_session) as printer:
        data = await printer.update()

    actual = to_json_safe(data)

    assert actual["online"] is True
    for key, value in load_expected(fixture_dir).items():
        assert actual[key] == value, f"{fixture_dir.name}: {key}"


async def test_update_tolerates_missing_optional_endpoints(
    mock_session: ClientSession, make_server: MakeServer
) -> None:
    """A model lacking every optional endpoint still completes `update()`."""
    server = await make_server(
        {
            path: route if path in REQUIRED_ENDPOINTS else RouteResponse(status=404)
            for path, route in fixture_routes(FULL_FIXTURE).items()
        }
    )

    async with _printer(server, mock_session) as printer:
        data = await printer.update()

    expected = load_expected(FULL_FIXTURE)

    assert data.online is True
    assert to_json_safe(data.device) == expected["device"]
    assert to_json_safe(data.status) == expected["status"]
    assert data.consumables == []
    assert data.printer_usage is None
    assert data.scanner_usage is None
    assert data.copy_usage is None
    assert data.fax_usage is None
    assert data.adapters == []
    assert data.eprint is None
    assert data.wifi is None
