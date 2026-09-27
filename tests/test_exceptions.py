# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for the aiohpprinter exception hierarchy."""

from __future__ import annotations

import pytest

from aiohpprinter.exceptions import (
    HpPrinterConnectionError,
    HpPrinterError,
    HpPrinterHttpError,
    HpPrinterParseError,
    HpPrinterTimeoutError,
    HpPrinterUnsupportedError,
)


@pytest.mark.parametrize(
    "exception_class",
    [
        HpPrinterConnectionError,
        HpPrinterTimeoutError,
        HpPrinterParseError,
        HpPrinterUnsupportedError,
    ],
    ids=lambda cls: cls.__name__,
)
def test_exception_is_a_hp_printer_error(
    exception_class: type[HpPrinterError],
) -> None:
    """Every specific exception is also catchable as `HpPrinterError`."""
    assert issubclass(exception_class, HpPrinterError)


def test_http_error_carries_the_status_code() -> None:
    """`HpPrinterHttpError` exposes the offending HTTP status code."""
    error = HpPrinterHttpError(404, "not found")

    assert error.status == 404  # noqa: PLR2004
    assert str(error) == "not found"
    assert isinstance(error, HpPrinterError)
