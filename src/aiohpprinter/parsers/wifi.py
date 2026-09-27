# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/DevMgmt/NetAppsSecureDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpWifi
from aiohpprinter.xml import get_path

from .common import text

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "NetAppsSecureDyn.WirelessDirectConfig"


def parse_wifi(document: dict[str, Any]) -> HpWifi:
    """Build Wireless Direct data from a `NetAppsSecureDyn` document."""
    config = get_path(document, _ROOT_PATH)

    return HpWifi(
        ssid_prefix=_decode_hex(text(config, "SSIDPrefix")),
        connection_method=text(config, "ConnectionMethod"),
    )


def _decode_hex(value: str | None) -> str | None:
    """Decode a hex-encoded string, as some models report the SSID prefix.

    Values that are not valid hex, or do not decode to printable text, are
    returned unchanged.
    """
    if value is None:
        return None

    try:
        decoded = bytes.fromhex(value).decode().strip()
    except ValueError:
        return value

    return decoded if decoded.isprintable() else value
