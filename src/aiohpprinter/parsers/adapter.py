# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/IoMgmt/Adapters`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpAdapter
from aiohpprinter.xml import get_path

from .common import boolean, text

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "Adapters.Adapter"


def parse_adapters(document: dict[str, Any]) -> list[HpAdapter]:
    """Build the list of network adapters from an `Adapters` document."""
    raw = get_path(document, _ROOT_PATH)

    if raw is None:
        return []

    items = raw if isinstance(raw, list) else [raw]

    return [_parse_item(item) for item in items if isinstance(item, dict)]


def _parse_item(item: dict[str, Any]) -> HpAdapter:
    return HpAdapter(
        name=text(item, "HardwareConfig.Name"),
        connectivity_port_type=text(item, "HardwareConfig.DeviceConnectivityPortType"),
        is_connected=boolean(item, "HardwareConfig.IsConnected", ("true",)),
    )
