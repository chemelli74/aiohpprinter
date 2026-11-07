# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Async Python library for HP printers exposing an embedded web server (EWS)."""

from .client import HpPrinter
from .exceptions import (
    HpPrinterConnectionError,
    HpPrinterError,
    HpPrinterHttpError,
    HpPrinterParseError,
    HpPrinterSslError,
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
    HpIOConfig,
    HpPreviousCartridge,
    HpPrinterData,
    HpPrinterDevice,
    HpPrinterStatus,
    HpPrinterUsage,
    HpScannerUsage,
    HpScanUsage,
    HpWifi,
)

__version__ = "3.6.0"

__all__ = [
    "HpAdapter",
    "HpConsumable",
    "HpConsumableColor",
    "HpCopyUsage",
    "HpDeviceStatus",
    "HpEPrint",
    "HpFaxUsage",
    "HpIOConfig",
    "HpPreviousCartridge",
    "HpPrinter",
    "HpPrinterConnectionError",
    "HpPrinterData",
    "HpPrinterDevice",
    "HpPrinterError",
    "HpPrinterHttpError",
    "HpPrinterParseError",
    "HpPrinterSslError",
    "HpPrinterStatus",
    "HpPrinterTimeoutError",
    "HpPrinterUnsupportedError",
    "HpPrinterUsage",
    "HpScanUsage",
    "HpScannerUsage",
    "HpWifi",
    "__version__",
]
