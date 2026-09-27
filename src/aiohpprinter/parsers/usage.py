# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parsers for the subunits of the ``/DevMgmt/ProductUsageDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpCopyUsage, HpFaxUsage, HpPrinterUsage, HpScannerUsage
from aiohpprinter.xml import get_path

from .common import integer

if TYPE_CHECKING:
    from typing import Any


def parse_printer_usage(document: dict[str, Any]) -> HpPrinterUsage:
    """Build printer engine counters from a `ProductUsageDyn` document."""
    subunit = get_path(document, "ProductUsageDyn.PrinterSubunit")

    return HpPrinterUsage(
        total_impressions=integer(subunit, "TotalImpressions"),
        monochrome_impressions=integer(subunit, "MonochromeImpressions"),
        color_impressions=integer(subunit, "ColorImpressions"),
        simplex_sheets=integer(subunit, "SimplexSheets"),
        duplex_sheets=integer(subunit, "DuplexSheets"),
        jam_events=integer(subunit, "JamEvents"),
        mispick_events=integer(subunit, "MispickEvents"),
    )


def parse_scanner_usage(document: dict[str, Any]) -> HpScannerUsage:
    """Build scanner engine counters from a `ProductUsageDyn` document."""
    subunit = get_path(document, "ProductUsageDyn.ScannerEngineSubunit")

    return HpScannerUsage(
        scan_images=integer(subunit, "ScanImages"),
        adf_images=integer(subunit, "AdfImages"),
        duplex_sheets=integer(subunit, "DuplexSheets"),
        flatbed_images=integer(subunit, "FlatbedImages"),
        jam_events=integer(subunit, "JamEvents"),
        mispick_events=integer(subunit, "MispickEvents"),
    )


def parse_copy_usage(document: dict[str, Any]) -> HpCopyUsage:
    """Build copy application counters from a `ProductUsageDyn` document."""
    subunit = get_path(document, "ProductUsageDyn.CopyApplicationSubunit")

    return HpCopyUsage(
        total_impressions=integer(subunit, "TotalImpressions"),
        adf_images=integer(subunit, "AdfImages"),
        flatbed_images=integer(subunit, "FlatbedImages"),
        monochrome_impressions=integer(subunit, "MonochromeImpressions"),
        color_impressions=integer(subunit, "ColorImpressions"),
    )


def parse_fax_usage(document: dict[str, Any]) -> HpFaxUsage:
    """Build fax application counters from a `ProductUsageDyn` document."""
    subunit = get_path(document, "ProductUsageDyn.FaxApplicationSubunit")

    return HpFaxUsage(
        total_impressions=integer(subunit, "TotalImpressions"),
    )
