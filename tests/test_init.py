# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for the aiohpprinter package's public surface."""

from __future__ import annotations

import aiohpprinter


def test_public_api_is_importable() -> None:
    """The documented public objects are importable from the package root."""
    assert isinstance(aiohpprinter.__version__, str)
    assert aiohpprinter.HpPrinter is not None
    assert issubclass(aiohpprinter.HpPrinterError, Exception)
    errors = aiohpprinter.HpPrinterError
    assert issubclass(aiohpprinter.HpPrinterConnectionError, errors)
    assert issubclass(aiohpprinter.HpPrinterTimeoutError, errors)
    assert issubclass(aiohpprinter.HpPrinterHttpError, errors)
    assert issubclass(aiohpprinter.HpPrinterParseError, errors)
    assert issubclass(aiohpprinter.HpPrinterUnsupportedError, errors)
