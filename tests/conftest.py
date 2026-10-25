# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Shared test fixtures for aiohpprinter."""

from __future__ import annotations

import asyncio
import dataclasses
import ssl
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import orjson
import pytest
from aiohttp import ClientSession, ClientTimeout, TCPConnector, web
from aiohttp.test_utils import TestServer

from aiohpprinter.client import HpPrinter
from aiohpprinter.const import (
    DEFAULT_TIMEOUT,
    ENDPOINT_ADAPTERS,
    ENDPOINT_CONSUMABLE_CONFIG,
    ENDPOINT_EPRINT_CONFIG,
    ENDPOINT_NET_APPS_SECURE,
    ENDPOINT_PRODUCT_CONFIG,
    ENDPOINT_PRODUCT_STATUS,
    ENDPOINT_PRODUCT_USAGE,
)
from aiohpprinter.xml import parse_document, parse_json_document

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Callable

FIXTURES_DIR = Path(__file__).parent / "fixtures"
#: A test CA and a `127.0.0.1` server certificate it signed. The CA key was
#: discarded; regenerate both with `openssl` if they ever need to change.
CERTS_DIR = Path(__file__).parent / "certs"
CA_CERT = CERTS_DIR / "ca.pem"

#: Endpoint URI to the filename a fixture directory stores its response
#: under. Used both by fixture-driven parser tests and by tests that need
#: to serve a fixture's XML back over a mocked HTTP call.
ENDPOINT_FILENAMES: dict[str, str] = {
    ENDPOINT_PRODUCT_CONFIG: "ProductConfigDyn.xml",
    ENDPOINT_PRODUCT_STATUS: "ProductStatusDyn.xml",
    ENDPOINT_CONSUMABLE_CONFIG: "ConsumableConfigDyn.xml",
    ENDPOINT_PRODUCT_USAGE: "ProductUsageDyn.xml",
    ENDPOINT_ADAPTERS: "Adapters.xml",
    ENDPOINT_EPRINT_CONFIG: "ePrintConfigDyn.xml",
    ENDPOINT_NET_APPS_SECURE: "NetAppsSecureDyn.xml",
}


def discover_fixtures() -> list[Path]:
    """Return every printer-model fixture directory under `tests/fixtures`.

    A new printer model becomes part of the regression suite simply by
    adding a directory here - no new test function is required.
    """
    return sorted(path for path in FIXTURES_DIR.iterdir() if path.is_dir())


def load_expected(fixture_dir: Path) -> dict[str, Any]:
    """Load a fixture's golden `expected.json`, or `{}` if it has none."""
    expected_path = fixture_dir / "expected.json"

    if not expected_path.exists():
        return {}

    return cast("dict[str, Any]", orjson.loads(expected_path.read_text()))


def load_xml(fixture_dir: Path, filename: str) -> str | None:
    """Load one XML file from a fixture directory, or `None` if absent."""
    xml_path = fixture_dir / filename

    if not xml_path.exists():
        return None

    return xml_path.read_text()


def load_document(fixture_dir: Path, filename: str) -> dict[str, Any] | None:
    """Parse one endpoint's response from a fixture directory, or `None`.

    Some models answer an endpoint as JSON instead of XML (observed on
    `/IoMgmt/Adapters`); the capture script stores those as `<stem>.json`.
    """
    document: dict[str, Any] | None = None
    json_path = fixture_dir / Path(filename).with_suffix(".json")

    if (xml := load_xml(fixture_dir, filename)) is not None:
        document = parse_document(xml)
    elif json_path.exists():
        document = parse_json_document(json_path.read_text())

    return document


def fixture_routes(
    fixture_dir: Path,
    *,
    missing_status: int | None = None,
) -> dict[str, RouteResponse]:
    """Build `make_server` routes for every endpoint a fixture directory covers.

    Endpoints without a file in `fixture_dir` are omitted unless
    `missing_status` is given, in which case they answer with that status
    (used to simulate a model that genuinely lacks an optional endpoint).
    """
    routes: dict[str, RouteResponse] = {}

    for endpoint, filename in ENDPOINT_FILENAMES.items():
        json_path = fixture_dir / Path(filename).with_suffix(".json")

        if (xml := load_xml(fixture_dir, filename)) is not None:
            routes[endpoint] = RouteResponse(body=xml)
        elif json_path.exists():
            routes[endpoint] = RouteResponse(
                body=json_path.read_text(), content_type="application/javascript"
            )
        elif missing_status is not None:
            routes[endpoint] = RouteResponse(status=missing_status)

    return routes


def to_json_safe(value: Any) -> Any:  # noqa: ANN401
    """Recursively convert models to the plain structures `expected.json` uses."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_json_safe(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }

    if isinstance(value, list):
        return [to_json_safe(item) for item in value]

    if isinstance(value, dict):
        return {key: to_json_safe(item) for key, item in value.items()}

    if isinstance(value, datetime):
        return value.isoformat()

    return value


@pytest.fixture
def anyio_backend() -> str:
    """Run async tests under asyncio only.

    They create real `aiohttp.ClientSession`/`aiohttp.test_utils.TestServer`
    instances, which require an asyncio event loop; anyio's default
    `anyio_backend` fixture parametrizes over every installed backend
    (including Trio, if it is ever pulled in), which would fail before any
    assertion runs.
    """
    return "asyncio"


@pytest.fixture
async def mock_session() -> AsyncGenerator[ClientSession]:
    """Return a real `ClientSession`, meant to be paired with `make_server`."""
    session = ClientSession()
    yield session
    await session.close()


@pytest.fixture
async def make_session() -> AsyncGenerator[Callable[[Path | None], ClientSession]]:
    """Yield a factory for `ClientSession`s trusting `cafile` on top of the system.

    Trusting `CA_CERT` makes the test server certificate a signed one;
    without it, the same certificate looks self-signed.
    """
    sessions: list[ClientSession] = []

    def _make(cafile: Path | None) -> ClientSession:
        context = ssl.create_default_context(cafile=cafile)
        sessions.append(ClientSession(connector=TCPConnector(ssl=context)))
        return sessions[-1]

    yield _make

    for session in sessions:
        await session.close()


@pytest.fixture
def server_ssl_context() -> ssl.SSLContext:
    """Return a server-side TLS context presenting the test certificate."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(CERTS_DIR / "server.pem", CERTS_DIR / "server.key")
    return context


@dataclasses.dataclass
class RouteResponse:
    """One canned HTTP response for `make_server` to serve at a given path."""

    status: int = 200
    body: str = ""
    content_type: str = "text/xml"
    delay: float = 0.0
    #: Raw bytes to send instead of `body`, e.g. to test malformed encodings.
    raw_body: bytes | None = None
    #: Extra response headers, e.g. a `Location` for a redirect.
    headers: dict[str, str] = dataclasses.field(default_factory=dict)


@pytest.fixture
async def make_server() -> AsyncGenerator[Callable[..., Awaitable[TestServer]]]:
    """Yield a factory that starts a local HTTP server serving canned routes.

    Pass `ssl_context` to serve HTTPS instead.

    A real (loopback) server is used instead of a transport-level mock:
    `aioresponses` is incompatible with the aiohttp version this project
    pins (its response builder omits `stream_writer`, now required by
    `aiohttp.ClientResponse.__init__`), and a real server exercises the
    client's actual HTTP handling - status codes, content types, and
    timeouts - rather than a re-implementation of it.
    """
    servers: list[TestServer] = []

    async def _make(
        routes: dict[str, RouteResponse], ssl_context: ssl.SSLContext | None = None
    ) -> TestServer:
        app = web.Application()

        for path, route in routes.items():
            app.router.add_get(path, _make_handler(route))

        server = TestServer(app)
        await server.start_server(ssl=ssl_context)
        servers.append(server)

        return server

    yield _make

    for server in servers:
        await server.close()


@pytest.fixture
def make_printer(
    mock_session: ClientSession,
    make_server: Callable[..., Awaitable[TestServer]],
) -> Callable[..., Awaitable[HpPrinter]]:
    """Return a factory serving `routes` and an `HpPrinter` pointed at them.

    `ssl_context` serves HTTPS and points the client at it with `ssl=True`;
    `session` replaces `mock_session`.
    """

    async def _make(
        routes: dict[str, RouteResponse],
        *,
        client_timeout: ClientTimeout = DEFAULT_TIMEOUT,
        session: ClientSession | None = None,
        ssl_context: ssl.SSLContext | None = None,
    ) -> HpPrinter:
        server = await make_server(routes, ssl_context)
        assert server.port is not None
        return HpPrinter(
            server.host,
            session=session or mock_session,
            port=server.port,
            ssl=ssl_context is not None,
            timeout=client_timeout,
        )

    return _make


def _make_handler(
    route: RouteResponse,
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(_request: web.Request) -> web.Response:
        if route.delay:
            await asyncio.sleep(route.delay)

        if route.raw_body is not None:
            return web.Response(
                status=route.status,
                body=route.raw_body,
                content_type=route.content_type,
                charset="utf-8",
                headers=route.headers,
            )

        return web.Response(
            status=route.status,
            text=route.body,
            content_type=route.content_type,
            headers=route.headers,
        )

    return handler
