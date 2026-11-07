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
    HpPrinterData,
    HpPrinterDevice,
    HpPrinterStatus,
    HpPrinterUsage,
    HpScannerUsage,
    HpWifi,
)

__version__ = "3.1.1"

__all__ = [
    "HpAdapter",
    "HpConsumable",
    "HpConsumableColor",
    "HpCopyUsage",
    "HpDeviceStatus",
    "HpEPrint",
    "HpFaxUsage",
    "HpIOConfig",
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
    "HpScannerUsage",
    "HpWifi",
    "__version__",
]
