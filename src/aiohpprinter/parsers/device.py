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

_ROOT_PATH = "ProductConfigDyn"
# Any other `PasswordStatus` value is unknown, not "no password".
_PASSWORD_STATUSES = {"set": True, "notset": False}


def parse_device(document: dict[str, Any]) -> HpPrinterDevice:
    """Build device identity data from a parsed `ProductConfigDyn` document."""
    root = get_path(document, _ROOT_PATH)
    info = get_path(root, "ProductInformation")
    settings = get_path(root, "ProductSettings")

    return HpPrinterDevice(
        make_and_model=text(info, "MakeAndModel"),
        make_and_model_family=text(info, "MakeAndModelFamily"),
        sku_identifier=text(info, "SKUIdentifier"),
        serial_number=text(info, "SerialNumber"),
        product_number=text(info, "ProductNumber"),
        manufacturer_name=text(info, "Manufacturer.Name"),
        manufactured_at=timestamp(info, "Manufacturer.Date"),
        firmware_revision=text(info, "Version.Revision"),
        firmware_date=timestamp(info, "Version.Date"),
        language_pack_version=text(info, "LanguagePackVersion.Revision"),
        admin_password_set=_PASSWORD_STATUSES.get(
            (text(info, "PasswordStatus") or "").lower()
        ),
        uuid=text(info, "UUID"),
        service_id=text(info, "ServiceID"),
        duplex_unit=text(info, "DuplexUnit"),
        # LaserJets report it as product information, inkjets as a setting.
        power_save=text(info, "PowerSave") or text(settings, "PowerSave"),
        friendly_name=text(settings, "FriendlyName"),
        power_save_timeout=text(settings, "PowerSaveTimeout"),
        shutdown_delay=text(settings, "ShutDownDelay"),
    )
