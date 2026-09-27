# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser merging the consumable config and usage endpoints.

Consumable data is split across two documents that describe the same
physical cartridges/tanks:

- ``/DevMgmt/ConsumableConfigDyn.xml`` - identity, warranty, life state.
- ``/DevMgmt/ProductUsageDyn.xml`` (``ConsumableSubunit``) - usage counters.

They are joined on a consumable label code: the config endpoint reports it
directly (``ConsumableLabelCode``, for example ``"C"``, ``"M"``, ``"K"``),
while the usage endpoint only reports a marker color (``"Cyan"``,
``"Magenta"``, ``"Black"``, ...) which is mapped to the same code via
:data:`aiohpprinter.const.MARKER_COLOR_TO_LABEL_CODE`.

Either endpoint may be unavailable on a given update cycle or unsupported by
a given printer model; consumables are still returned from whichever side
did respond.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from aiohpprinter.const import MARKER_COLOR_TO_LABEL_CODE
from aiohpprinter.models import HpConsumable
from aiohpprinter.xml import get_path

from .common import integer, number, text, timestamp

if TYPE_CHECKING:
    from typing import Any

_CONFIG_ROOT_PATH = "ConsumableConfigDyn.ConsumableInfo"
_USAGE_ROOT_PATH = "ProductUsageDyn.ConsumableSubunit.Consumable"


def parse_consumables(
    config_document: dict[str, Any] | None,
    usage_document: dict[str, Any] | None,
) -> list[HpConsumable]:
    """Build the merged list of consumables from the two source documents."""
    consumables: dict[str, HpConsumable] = {}

    for item in _as_list(get_path(config_document, _CONFIG_ROOT_PATH)):
        parsed = _parse_config_item(item)
        if parsed is not None:
            consumables[parsed.consumable_id] = parsed

    for item in _as_list(get_path(usage_document, _USAGE_ROOT_PATH)):
        consumable_id, usage = _parse_usage_item(item)
        if consumable_id is None:
            continue

        existing = consumables.get(consumable_id)
        consumables[consumable_id] = (
            _merge(existing, usage) if existing is not None else usage
        )

    return [consumables[key] for key in sorted(consumables)]


def _as_list(value: Any) -> list[Any]:  # noqa: ANN401
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _parse_config_item(item: Any) -> HpConsumable | None:  # noqa: ANN401
    if not isinstance(item, dict):
        return None

    consumable_id = text(item, "ConsumableLabelCode")
    if consumable_id is None:
        return None

    return HpConsumable(
        consumable_id=consumable_id,
        consumable_type=text(item, "ConsumableTypeEnum"),
        state=text(item, "ConsumableLifeState.ConsumableState"),
        brand=text(item, "ConsumableLifeState.Brand"),
        station=text(item, "ConsumableStation"),
        percentage_level_remaining=number(item, "ConsumablePercentageLevelRemaining"),
        max_capacity=number(item, "Capacity.MaxCapacity"),
        selectibility_number=text(item, "ConsumableSelectibilityNumber"),
        manufacturer_name=text(item, "Manufacturer.Name"),
        manufactured_at=timestamp(item, "Manufacturer.Date"),
        installed_at=timestamp(item, "Installation.Date"),
        warranty_expires_at=timestamp(item, "Warranty.ExpirationDate"),
        serial_number=text(item, "SerialNumber"),
        product_number=text(item, "ProductNumber"),
        unique_id=text(item, "ConsumableUniqueID"),
    )


def _parse_usage_item(item: Any) -> tuple[str | None, HpConsumable]:  # noqa: ANN401
    marker_color = text(item, "MarkerColor") if isinstance(item, dict) else None
    consumable_id = (
        MARKER_COLOR_TO_LABEL_CODE.get(marker_color, marker_color)
        if marker_color
        else None
    )

    usage = HpConsumable(
        consumable_id=consumable_id or "",
        consumable_type=text(item, "ConsumableTypeEnum"),
        marker_color=marker_color,
        usage_state=text(item, "ConsumableState"),
        station=text(item, "ConsumableStation"),
        raw_percentage_level_remaining=number(
            item, "ConsumableRawPercentageLevelRemaining"
        ),
        estimated_pages_remaining=integer(item, "EstimatedPagesRemaining"),
        supply_serial_number=text(item, "SupplySerialNumber"),
        counterfeit_refilled_count=integer(
            item, "RefilledCount.CounterfeitRefilledCount"
        ),
        genuine_refilled_count=integer(item, "RefilledCount.GenuineRefilledCount"),
        total_impressions=integer(item, "TotalImpressions"),
    )

    return consumable_id, usage


def _merge(config: HpConsumable, usage: HpConsumable) -> HpConsumable:
    return replace(
        config,
        consumable_type=config.consumable_type or usage.consumable_type,
        marker_color=usage.marker_color,
        usage_state=usage.usage_state,
        station=config.station or usage.station,
        raw_percentage_level_remaining=usage.raw_percentage_level_remaining,
        estimated_pages_remaining=usage.estimated_pages_remaining,
        supply_serial_number=usage.supply_serial_number,
        counterfeit_refilled_count=usage.counterfeit_refilled_count,
        genuine_refilled_count=usage.genuine_refilled_count,
        total_impressions=usage.total_impressions,
    )
