# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Typed printer-domain models returned by :class:`aiohpprinter.HpPrinter`.

These describe HP printer concepts (device identity, status, consumables,
usage counters, ...), not Home Assistant entities. Every field is optional
unless the printer protocol guarantees it, since firmware and product
generation determine which elements a given model actually reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class HpPrinterDevice:
    """Identity information for the printer as a whole."""

    make_and_model: str | None = None
    make_and_model_family: str | None = None
    sku_identifier: str | None = None
    serial_number: str | None = None
    product_number: str | None = None
    manufacturer_name: str | None = None
    manufactured_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class HpPrinterStatus:
    """The printer's current operational status."""

    device_status: str | None = None

    @property
    def is_ready(self) -> bool:
        """Return whether the printer is idle and ready to accept jobs."""
        return self.device_status == "ready"

    @property
    def is_off(self) -> bool:
        """Return whether the printer is powered off or unreachable."""
        return self.device_status is None or self.device_status == "off"


@dataclass(frozen=True, slots=True)
class HpConsumable:
    """A single ink/toner consumable, merged from config and usage data.

    ``consumable_id`` is the value the two source endpoints are joined on:
    the consumable label code (for example ``"C"``, ``"M"``, ``"Y"``,
    ``"K"``, or ``"CMY"`` for a combined cartridge).
    """

    consumable_id: str
    consumable_type: str | None = None
    marker_color: str | None = None
    state: str | None = None
    usage_state: str | None = None
    brand: str | None = None
    station: str | None = None
    percentage_level_remaining: float | None = None
    raw_percentage_level_remaining: float | None = None
    estimated_pages_remaining: int | None = None
    max_capacity: float | None = None
    selectibility_number: str | None = None
    manufacturer_name: str | None = None
    manufactured_at: datetime | None = None
    installed_at: datetime | None = None
    warranty_expires_at: datetime | None = None
    serial_number: str | None = None
    product_number: str | None = None
    supply_serial_number: str | None = None
    unique_id: str | None = None
    counterfeit_refilled_count: int | None = None
    genuine_refilled_count: int | None = None
    total_impressions: int | None = None

    @property
    def is_ok(self) -> bool:
        """Return whether the consumable reports a healthy life state."""
        return self.state in {"ok", "newGenuineHP"}


@dataclass(frozen=True, slots=True)
class HpPrinterUsage:
    """Cumulative page counters for the printer engine."""

    total_impressions: int | None = None
    monochrome_impressions: int | None = None
    color_impressions: int | None = None
    simplex_sheets: int | None = None
    duplex_sheets: int | None = None
    jam_events: int | None = None
    mispick_events: int | None = None


@dataclass(frozen=True, slots=True)
class HpScannerUsage:
    """Cumulative page counters for the scanner engine."""

    scan_images: int | None = None
    adf_images: int | None = None
    duplex_sheets: int | None = None
    flatbed_images: int | None = None
    jam_events: int | None = None
    mispick_events: int | None = None


@dataclass(frozen=True, slots=True)
class HpCopyUsage:
    """Cumulative page counters for the copy application."""

    total_impressions: int | None = None
    adf_images: int | None = None
    flatbed_images: int | None = None
    monochrome_impressions: int | None = None
    color_impressions: int | None = None


@dataclass(frozen=True, slots=True)
class HpFaxUsage:
    """Cumulative page counters for the fax application."""

    total_impressions: int | None = None


@dataclass(frozen=True, slots=True)
class HpAdapter:
    """A network adapter reported by the printer's I/O management."""

    name: str | None = None
    connectivity_port_type: str | None = None
    is_connected: bool | None = None


@dataclass(frozen=True, slots=True)
class HpEPrint:
    """HP ePrint cloud printing configuration."""

    printer_id: str | None = None
    is_registered: bool | None = None
    cloud_services_enabled: bool | None = None


@dataclass(frozen=True, slots=True)
class HpWifi:
    """Wireless Direct configuration."""

    ssid_prefix: str | None = None
    connection_method: str | None = None


@dataclass(frozen=True, slots=True)
class HpPrinterData:
    """Aggregate snapshot of everything :meth:`HpPrinter.update` collected.

    Every section besides ``online`` is `None` (or an empty list) when its
    endpoint is not supported by this printer model, or could not be
    retrieved on this update cycle - see the client's optional-endpoint
    handling for details.
    """

    online: bool
    device: HpPrinterDevice | None = None
    status: HpPrinterStatus | None = None
    consumables: list[HpConsumable] = field(default_factory=list)
    printer_usage: HpPrinterUsage | None = None
    scanner_usage: HpScannerUsage | None = None
    copy_usage: HpCopyUsage | None = None
    fax_usage: HpFaxUsage | None = None
    adapters: list[HpAdapter] = field(default_factory=list)
    eprint: HpEPrint | None = None
    wifi: HpWifi | None = None
