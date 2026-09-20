# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""aiohpprinter library exceptions."""

from __future__ import annotations


class HpPrinterError(Exception):
    """Base class for aiohpprinter errors."""


class CannotConnect(HpPrinterError):
    """Exception raised when connection fails."""


class GenericResponseError(HpPrinterError):
    """Exception raised when a request returns an unexpected response."""
