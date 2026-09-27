# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Capture a real printer's EWS responses as a `tests/fixtures/<model>/` set.

Usage:

    python scripts/capture_fixture.py 192.168.1.100 [--model "HP OfficeJet Pro 9022e"]

Every endpoint `aiohpprinter` reads is fetched, plus every resource the
printer advertises in `/DevMgmt/DiscoveryTree.xml` (useful when adding
parser support for new fields later). Identifying values are redacted, and
an `expected.json` golden file is generated from what the current parsers
return for the sanitized documents - review it before committing.
"""

import asyncio
import dataclasses
import json
import re
import shutil
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree.ElementTree import ParseError

import aiohttp
from defusedxml.ElementTree import fromstring

from aiohpprinter.const import (
    ENDPOINT_ADAPTERS,
    ENDPOINT_CONSUMABLE_CONFIG,
    ENDPOINT_EPRINT_CONFIG,
    ENDPOINT_NET_APPS_SECURE,
    ENDPOINT_PRODUCT_CONFIG,
    ENDPOINT_PRODUCT_STATUS,
    ENDPOINT_PRODUCT_USAGE,
)
from aiohpprinter.exceptions import HpPrinterParseError
from aiohpprinter.parsers import (
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
from aiohpprinter.xml import parse_document, parse_json_document

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"
ENDPOINT_DISCOVERY_TREE = "/DevMgmt/DiscoveryTree.xml"

LIBRARY_ENDPOINTS = (
    ENDPOINT_PRODUCT_STATUS,
    ENDPOINT_PRODUCT_CONFIG,
    ENDPOINT_CONSUMABLE_CONFIG,
    ENDPOINT_PRODUCT_USAGE,
    ENDPOINT_ADAPTERS,
    ENDPOINT_EPRINT_CONFIG,
    ENDPOINT_NET_APPS_SECURE,
)

JSON_CONTENT_TYPE = "application/javascript"
REDACTED = "REDACTED"

#: Local element/key names whose value identifies the printer, its owner or
#: its network, matched case-insensitively against the whole name.
SENSITIVE_NAMES = re.compile(
    r"(?i)^("
    r"\w*SerialNumber|PrinterID|\w*UUID|\w*Unique\w*ID|"
    r"ConsumableID|ConsumableRawData|\w*Signature|"
    r"MacAddress|HardwareAddress|\w*BSSID|SSID|"
    r"IP(v[46])?Address|\w*Gateway|DNSServer\w*|"
    r"Host[Nn]ame|DomainName|FQDN|BonjourServiceName|"
    r"\w*UserID|\w*UserName|\w*JobName|"
    r"\w*EmailAddress|Email|(?!Show)\w*Passphrase|\w*Password|PreSharedKey|PIN|"
    r"FriendlyName|\w*Contact\w*|Location|DeviceLocation|AssetNumber|CompanyName|"
    r"Latitude|Longitude|\w*RequesterID|\w*DeviceInfoDeviceID"
    r")$"
)
#: IP-literal hosts in URLs (e.g. the EWS `ResourceURI` entries).
URL_IP_HOST = re.compile(r"(?i)(?<=://)(\[[0-9a-f:.%]+\]|(?:\d{1,3}\.){3}\d{1,3})")
#: Compressed IPv6 addresses; link-local ones embed the printer's MAC.
IPV6_ADDRESS = re.compile(
    r"(?i)(?<![\w:.])(?=[0-9a-f:]*::)(?:[0-9a-f]{1,4})?(?::[0-9a-f]{0,4}){2,7}(?![\w:.])"
)
XML_ELEMENT = re.compile(
    r"(<(?:[\w.-]+:)?(?P<name>[\w.-]+)(?:\s[^>]*)?>)(?P<value>[^<]+)(</)"
)
SERIES_MODEL = re.compile(
    r"(?i)^(?P<prefix>.*?)(?P<number>\d{3,})(?P<suffix>.*?)\s+series$"
)
MAC_ADDRESS = re.compile(r"\b[0-9A-Fa-f]{2}(?:[:-][0-9A-Fa-f]{2}){5}\b")
#: The `SN:<value>;` field inside an IEEE 1284 device ID string (as embedded
#: in `ShopForSupplies.xml`'s `DeviceInfoData`), which repeats the serial
#: number already redacted from `DeviceInfoDeviceID`/`RequesterID`.
DEVICE_ID_SERIAL = re.compile(r"(?i)(?<=;SN:)[^;]+(?=;)")


@dataclasses.dataclass
class Capture:
    """One endpoint response as saved to the fixture directory."""

    filename: str
    content: str
    is_json: bool


def get_arguments() -> Namespace:
    """Parse command line arguments."""
    parser = ArgumentParser(description="Capture an aiohpprinter test fixture")
    parser.add_argument("host", help="Printer IP address or hostname")
    parser.add_argument(
        "--model",
        help='Printer model, e.g. "HP OfficeJet Pro 9022e" '
        "(default: derived from ProductConfigDyn.xml)",
    )
    parser.add_argument("--port", type=int, default=None, help="EWS port")
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS for the EWS")
    parser.add_argument(
        "--no-discovery",
        action="store_true",
        help="Only fetch the endpoints aiohpprinter reads, skip DiscoveryTree.xml",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing fixture dir"
    )
    return parser.parse_args()


def detect_model(captures: dict[str, Capture]) -> str | None:
    """Return the exact model name reported by `ProductConfigDyn.xml`.

    Many models only report their family as `MakeAndModel` (e.g. "HP
    OfficeJet Pro 9020 series", "ENVY Photo 7800 All-in-One Printer
    series") and the variant as `SKUIdentifier` (e.g. "9022e", "7830"). The
    SKU replaces the series number only when it is a variant of it, since
    other models put a product code (e.g. "1MR78B") there. Names without
    the manufacturer get it prefixed.
    """
    if (capture := captures.get(ENDPOINT_PRODUCT_CONFIG)) is None:
        return None

    device = parse_device(parse_document(capture.content))
    make_and_model: str | None = device.make_and_model
    if make_and_model is None:
        return None

    series = SERIES_MODEL.match(make_and_model)
    sku = device.sku_identifier
    if series and sku and sku.lower().startswith(series["number"].rstrip("0")):
        make_and_model = f"{series['prefix']}{sku}{series['suffix']}"

    manufacturer: str | None = device.manufacturer_name
    if manufacturer and not make_and_model.lower().startswith(manufacturer.lower()):
        make_and_model = f"{manufacturer} {make_and_model}"

    return make_and_model


def model_slug(model: str) -> str:
    """Return the fixture directory name for `model`."""
    return re.sub(r"[^a-z0-9]+", "_", model.lower()).strip("_")


def filename_for(endpoint: str, *, is_json: bool) -> str:
    """Return the fixture filename `tests/conftest.py` expects for `endpoint`."""
    name = PurePosixPath(endpoint).name
    stem = name.removesuffix(".xml")
    return f"{stem}.json" if is_json else f"{stem}.xml"


def sanitize_xml(content: str) -> str:
    """Redact identifying element values, keeping the document structure."""

    def _replace(match: re.Match[str]) -> str:
        if not SENSITIVE_NAMES.match(match["name"]) or not match["value"].strip():
            return match[0]
        return f"{match[1]}{REDACTED}{match[4]}"

    return redact_addresses(XML_ELEMENT.sub(_replace, content))


def redact_addresses(content: str) -> str:
    """Redact MAC/IP addresses and embedded device-ID serials in `content`."""
    content = URL_IP_HOST.sub(REDACTED, content)
    content = IPV6_ADDRESS.sub(REDACTED, content)
    content = MAC_ADDRESS.sub(REDACTED, content)
    return DEVICE_ID_SERIAL.sub(REDACTED, content)


def sanitize_json(value: Any) -> Any:  # noqa: ANN401
    """Redact identifying values from a decoded JSON response."""
    if isinstance(value, dict):
        return {
            key: REDACTED
            if SENSITIVE_NAMES.match(key) and isinstance(item, str | int)
            else sanitize_json(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_json(item) for item in value]
    if isinstance(value, str):
        return redact_addresses(value)
    return value


async def fetch(
    session: aiohttp.ClientSession, base_url: str, endpoint: str
) -> Capture | None:
    """Fetch and sanitize `endpoint`, or return `None` if it is unusable."""
    url = f"{base_url}{endpoint}"
    try:
        async with session.get(url) as response:
            if response.status >= 400:  # noqa: PLR2004
                print(f"  {endpoint}: HTTP {response.status}, skipped")
                return None
            content = (await response.text()).replace("\r\n", "\n")
            content_type = response.content_type
    except (TimeoutError, aiohttp.ClientError) as ex:
        print(f"  {endpoint}: {type(ex).__name__} {ex}, skipped")
        return None

    is_json = content_type == JSON_CONTENT_TYPE
    try:
        if is_json:
            content = json.dumps(sanitize_json(json.loads(content)), indent=2) + "\n"
            parse_json_document(content)
        else:
            content = sanitize_xml(content)
            parse_document(content)
    except (json.JSONDecodeError, HpPrinterParseError) as ex:
        print(f"  {endpoint}: not a parsable document ({ex}), skipped")
        return None

    print(f"  {endpoint}: OK")
    return Capture(filename_for(endpoint, is_json=is_json), content, is_json)


def discovered_endpoints(content: str) -> list[str]:
    """Return every resource URI advertised by `DiscoveryTree.xml`."""
    try:
        root = fromstring(content)
    except ParseError:
        return []
    return sorted(
        {
            uri
            for element in root.iter()
            if element.tag.rsplit("}", 1)[-1] == "ResourceURI"
            and (uri := (element.text or "").strip()).startswith("/")
        }
    )


def to_json_safe(value: Any) -> Any:  # noqa: ANN401
    """Recursively convert models to the plain structures `expected.json` uses."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_json_safe(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, list):
        return [to_json_safe(item) for item in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def build_expected(captures: dict[str, Capture]) -> dict[str, Any]:
    """Parse the sanitized library endpoints into `expected.json` content."""
    documents: dict[str, dict[str, Any]] = {}
    for endpoint in LIBRARY_ENDPOINTS:
        if capture := captures.get(endpoint):
            parse = parse_json_document if capture.is_json else parse_document
            documents[endpoint] = parse(capture.content)

    expected: dict[str, Any] = {}
    if document := documents.get(ENDPOINT_PRODUCT_CONFIG):
        expected["device"] = parse_device(document)
    if document := documents.get(ENDPOINT_PRODUCT_STATUS):
        expected["status"] = parse_status(document)
    config = documents.get(ENDPOINT_CONSUMABLE_CONFIG)
    usage = documents.get(ENDPOINT_PRODUCT_USAGE)
    if config or usage:
        expected["consumables"] = parse_consumables(config, usage)
    if usage:
        expected["printer_usage"] = parse_printer_usage(usage)
        expected["scanner_usage"] = parse_scanner_usage(usage)
        expected["copy_usage"] = parse_copy_usage(usage)
        expected["fax_usage"] = parse_fax_usage(usage)
    if document := documents.get(ENDPOINT_ADAPTERS):
        expected["adapters"] = parse_adapters(document)
    if document := documents.get(ENDPOINT_EPRINT_CONFIG):
        expected["eprint"] = parse_eprint(document)
    if document := documents.get(ENDPOINT_NET_APPS_SECURE):
        expected["wifi"] = parse_wifi(document)

    return {key: to_json_safe(value) for key, value in expected.items()}


def readme(model: str, slug: str, captures: dict[str, Capture]) -> str:
    """Return the provenance `README.md` for the fixture directory."""
    files = "\n".join(f"- `{c.filename}` ({e})" for e, c in sorted(captures.items()))
    return (
        f"# {slug}\n\n"
        "**Provenance: real, captured** with `scripts/capture_fixture.py`.\n\n"
        f"Printer model: **{model}**\n\n"
        f"{files}\n\n"
        "## Sanitization\n\n"
        f"Identifying values (serial numbers, IDs, MAC/IP addresses, hostnames, "
        f"SSIDs, e-mail addresses, credentials) were replaced with `{REDACTED}` "
        "by the capture script. Review the files before committing.\n"
    )


async def capture(args: Namespace) -> dict[str, Capture] | None:
    """Fetch every endpoint, or return `None` if the printer is unusable."""
    protocol = "https" if args.ssl else "http"
    port = args.port or (443 if args.ssl else 80)
    base_url = f"{protocol}://{args.host}:{port}"
    print(f"Capturing from {base_url}")

    connector = aiohttp.TCPConnector(ssl=False)  # EWS certificates are self-signed
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        captures: dict[str, Capture] = {}
        for endpoint in LIBRARY_ENDPOINTS:
            if result := await fetch(session, base_url, endpoint):
                captures[endpoint] = result

        if ENDPOINT_PRODUCT_STATUS not in captures:
            print(f"{ENDPOINT_PRODUCT_STATUS} is required but was not captured")
            return None

        if not args.no_discovery and (
            tree := await fetch(session, base_url, ENDPOINT_DISCOVERY_TREE)
        ):
            captures[ENDPOINT_DISCOVERY_TREE] = tree
            for endpoint in discovered_endpoints(tree.content):
                if endpoint not in captures and (
                    result := await fetch(session, base_url, endpoint)
                ):
                    captures[endpoint] = result

    return captures


def write_fixture(model: str, fixture_dir: Path, captures: dict[str, Capture]) -> None:
    """Write the captured documents, `expected.json` and `README.md`."""
    used_names: set[str] = set()
    fixture_dir.mkdir(parents=True, exist_ok=True)
    for endpoint, result in captures.items():
        if result.filename in used_names:
            # Same basename under a different EWS tree: qualify it by path.
            result.filename = "_".join(PurePosixPath(endpoint).parts[1:])
        used_names.add(result.filename)
        (fixture_dir / result.filename).write_text(result.content, encoding="utf-8")

    (fixture_dir / "expected.json").write_text(
        json.dumps(build_expected(captures), indent=2) + "\n", encoding="utf-8"
    )
    (fixture_dir / "README.md").write_text(
        readme(model, fixture_dir.name, captures), encoding="utf-8"
    )

    print(f"Wrote {len(captures)} documents to {fixture_dir}")
    print("Review the redaction and expected.json, then run: uv run pytest")


def main() -> None:
    """Run the capture."""
    args = get_arguments()

    if (captures := asyncio.run(capture(args))) is None:
        sys.exit(1)

    if (model := args.model or detect_model(captures)) is None:
        print("Could not detect the printer model, pass it with --model")
        sys.exit(1)

    fixture_dir = FIXTURES_DIR / model_slug(model)
    if fixture_dir.exists():
        if not args.force:
            print(f"{fixture_dir} already exists, pass --force to overwrite it")
            sys.exit(1)
        # Drop any files from a previous capture that the printer no longer
        # answers for, so stale fixtures can't outlive this run's expected.json.
        shutil.rmtree(fixture_dir)

    print(f"Printer model: {model}")
    write_fixture(model, fixture_dir, captures)


if __name__ == "__main__":
    main()
