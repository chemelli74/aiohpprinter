# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Async Python library for HP printers exposing an embedded web server (EWS)."""

from .client import HpPrinter
from .exceptions import (
    HpPrinterConnectionError,
    HpPrinterError,
    HpPrinterHttpError,
    HpPrinterParseError,
    HpPrinterTimeoutError,
    HpPrinterUnsupportedError,
)
from .models import (
    HpAdapter,
    HpConsumable,
    HpConsumableColor,
    HpCopyUsage,
    HpDeviceStatus,
    HpEPrint,
    HpFaxUsage,
    HpPrinterData,
    HpPrinterDevice,
    HpPrinterStatus,
    HpPrinterUsage,
    HpScannerUsage,
    HpWifi,
)

__version__ = "1.0.1"

__all__ = [
    "HpAdapter",
    "HpConsumable",
    "HpConsumableColor",
    "HpCopyUsage",
    "HpDeviceStatus",
    "HpEPrint",
    "HpFaxUsage",
    "HpPrinter",
    "HpPrinterConnectionError",
    "HpPrinterData",
    "HpPrinterDevice",
    "HpPrinterError",
    "HpPrinterHttpError",
    "HpPrinterParseError",
    "HpPrinterStatus",
    "HpPrinterTimeoutError",
    "HpPrinterUnsupportedError",
    "HpPrinterUsage",
    "HpScannerUsage",
    "HpWifi",
    "__version__",
]
