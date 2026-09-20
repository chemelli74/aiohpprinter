# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Base tests for aiohpprinter."""

from aiohpprinter import __version__
from aiohpprinter.api import HpPrinterApi, HpPrinterDevice
from aiohpprinter.exceptions import (
    CannotConnect,
    GenericResponseError,
    HpPrinterError,
)


def test_objects_can_be_imported() -> None:
    """Verify objects exist."""
    assert isinstance(__version__, str)
    assert type(CannotConnect)
    assert type(GenericResponseError)
    assert type(HpPrinterError)
    assert type(HpPrinterApi)
    assert type(HpPrinterDevice)
