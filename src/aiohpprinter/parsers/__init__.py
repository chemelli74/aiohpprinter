# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Pure, synchronous XML-to-model parsers, one module per EWS endpoint.

Parsing in-memory XML/dict data is not I/O, so unlike the HTTP client these
functions are plain synchronous callables. Each takes the dict produced by
:func:`aiohpprinter.xml.parse_document` and returns typed models from
:mod:`aiohpprinter.models`.
"""

from __future__ import annotations

from .adapter import parse_adapters
from .consumable import parse_consumables
from .device import parse_device
from .eprint import parse_eprint
from .status import parse_status
from .usage import (
    parse_copy_usage,
    parse_fax_usage,
    parse_printer_usage,
    parse_scanner_usage,
)
from .wifi import parse_wifi

__all__ = [
    "parse_adapters",
    "parse_consumables",
    "parse_copy_usage",
    "parse_device",
    "parse_eprint",
    "parse_fax_usage",
    "parse_printer_usage",
    "parse_scanner_usage",
    "parse_status",
    "parse_wifi",
]
