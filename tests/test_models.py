# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for model default values and small convenience properties."""

from __future__ import annotations

from aiohpprinter.models import HpConsumable, HpPrinterData, HpPrinterStatus


def test_printer_status_is_ready_only_for_ready_category() -> None:
    """`is_ready` is `True` only for the `"ready"` status category."""
    assert HpPrinterStatus(device_status="ready").is_ready is True
    assert HpPrinterStatus(device_status="processing").is_ready is False


def test_printer_status_is_off_for_off_and_unknown() -> None:
    """`is_off` covers both an explicit `"off"` category and no data at all."""
    assert HpPrinterStatus(device_status="off").is_off is True
    assert HpPrinterStatus(device_status=None).is_off is True
    assert HpPrinterStatus(device_status="ready").is_off is False


def test_consumable_is_ok_for_known_healthy_states() -> None:
    """`is_ok` accepts both healthy life-state values the printer reports."""
    assert HpConsumable(consumable_id="K", state="ok").is_ok is True
    assert HpConsumable(consumable_id="K", state="newGenuineHP").is_ok is True
    assert HpConsumable(consumable_id="K", state="low").is_ok is False
    assert HpConsumable(consumable_id="K", state=None).is_ok is False


def test_printer_data_defaults_to_empty_optional_sections() -> None:
    """An offline snapshot defaults every optional section to empty/`None`."""
    data = HpPrinterData(online=False)

    assert data.device is None
    assert data.status is None
    assert data.consumables == []
    assert data.printer_usage is None
    assert data.scanner_usage is None
    assert data.copy_usage is None
    assert data.fax_usage is None
    assert data.adapters == []
    assert data.eprint is None
    assert data.wifi is None
