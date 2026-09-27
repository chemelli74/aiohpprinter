# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/DevMgmt/ProductConfigDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpPrinterDevice
from aiohpprinter.xml import get_path

from .common import text, timestamp

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "ProductConfigDyn.ProductInformation"


def parse_device(document: dict[str, Any]) -> HpPrinterDevice:
    """Build device identity data from a parsed `ProductConfigDyn` document."""
    info = get_path(document, _ROOT_PATH)

    return HpPrinterDevice(
        make_and_model=text(info, "MakeAndModel"),
        make_and_model_family=text(info, "MakeAndModelFamily"),
        sku_identifier=text(info, "SKUIdentifier"),
        serial_number=text(info, "SerialNumber"),
        product_number=text(info, "ProductNumber"),
        manufacturer_name=text(info, "Manufacturer.Name"),
        manufactured_at=timestamp(info, "Manufacturer.Date"),
    )
