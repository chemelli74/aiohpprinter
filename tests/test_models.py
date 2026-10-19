# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for model default values and small convenience properties."""

from __future__ import annotations

import logging

import pytest

from aiohpprinter.models import (
    HpConsumable,
    HpConsumableColor,
    HpDeviceStatus,
    HpPrinterData,
    HpPrinterStatus,
)


def test_printer_status_is_ready_only_for_ready_category() -> None:
    """`is_ready` is `True` only for the `"ready"` status category."""
    assert HpPrinterStatus(device_status="ready").is_ready is True
    assert HpPrinterStatus(device_status="processing").is_ready is False


def test_printer_status_is_off_for_off_and_unknown() -> None:
    """`is_off` covers both an explicit `"off"` category and no data at all."""
    assert HpPrinterStatus(device_status="off").is_off is True
    assert HpPrinterStatus(device_status=None).is_off is True
    assert HpPrinterStatus(device_status="ready").is_off is False


@pytest.mark.parametrize(
    ("device_status", "expected"),
    [
        pytest.param("canceljob", HpDeviceStatus.CANCEL_JOB, id="canceljob"),
        pytest.param("copying", HpDeviceStatus.COPYING, id="copying"),
        pytest.param("inpowersave", HpDeviceStatus.IN_POWER_SAVE, id="inpowersave"),
        pytest.param("off", HpDeviceStatus.OFF, id="off"),
        pytest.param("processing", HpDeviceStatus.PROCESSING, id="processing"),
        pytest.param("ready", HpDeviceStatus.READY, id="ready"),
        pytest.param(
            "scanprocessing", HpDeviceStatus.SCAN_PROCESSING, id="scanprocessing"
        ),
        pytest.param("trayempty", HpDeviceStatus.TRAY_EMPTY, id="trayempty"),
        pytest.param(None, None, id="missing"),
    ],
)
def test_printer_status_maps_known_categories(
    device_status: str | None, expected: HpDeviceStatus | None
) -> None:
    """`status` maps each known raw category to its snake_case enum member."""
    assert HpPrinterStatus(device_status=device_status).status is expected


def test_printer_status_unknown_category_is_logged(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An unknown category maps to `None` and is logged for bug reports."""
    with caplog.at_level(logging.DEBUG, logger="aiohpprinter"):
        assert HpPrinterStatus(device_status="somethingnew").status is None

    assert "Unknown device status: somethingnew" in caplog.text


@pytest.mark.parametrize(
    ("consumable_id", "expected"),
    [
        pytest.param("C", HpConsumableColor.CYAN, id="cyan"),
        pytest.param("M", HpConsumableColor.MAGENTA, id="magenta"),
        pytest.param("Y", HpConsumableColor.YELLOW, id="yellow"),
        pytest.param("K", HpConsumableColor.BLACK, id="black"),
        pytest.param("CMY", HpConsumableColor.TRI_COLOR, id="tri_color"),
        pytest.param("CMYK", None, id="printhead"),
    ],
)
def test_consumable_color(
    consumable_id: str, expected: HpConsumableColor | None
) -> None:
    """`color` maps the consumable label code to its snake_case enum member."""
    assert HpConsumable(consumable_id=consumable_id).color is expected


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
    assert data.consumables == {}
    assert data.printer_usage is None
    assert data.scanner_usage is None
    assert data.copy_usage is None
    assert data.fax_usage is None
    assert data.adapters == []
    assert data.eprint is None
    assert data.wifi is None
