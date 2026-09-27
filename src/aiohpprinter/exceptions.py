# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""aiohpprinter library exceptions."""

from __future__ import annotations


class HpPrinterError(Exception):
    """Base class for all aiohpprinter errors."""


class HpPrinterConnectionError(HpPrinterError):
    """Raised when the printer cannot be reached over the network."""


class HpPrinterTimeoutError(HpPrinterError):
    """Raised when a request to the printer times out."""


class HpPrinterHttpError(HpPrinterError):
    """Raised when the printer returns an unsuccessful HTTP status code."""

    def __init__(self, status: int, message: str) -> None:
        """Initialize the error with the offending HTTP status code."""
        super().__init__(message)
        self.status = status


class HpPrinterParseError(HpPrinterError):
    """Raised when a printer response cannot be parsed as valid XML."""


class HpPrinterUnsupportedError(HpPrinterError):
    """Raised when the printer does not expose a required endpoint."""
