# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/ePrint/ePrintConfigDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpEPrint
from aiohpprinter.xml import get_path

from .common import boolean, text

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "ePrintConfigDyn"


def parse_eprint(document: dict[str, Any]) -> HpEPrint:
    """Build ePrint cloud printing data from an `ePrintConfigDyn` document."""
    config = get_path(document, _ROOT_PATH)

    return HpEPrint(
        printer_id=text(config, "PrinterID"),
        is_registered=boolean(config, "RegistrationState", ("registered",)),
        cloud_services_enabled=boolean(
            config, "CloudServicesSwitch.Status", ("enabled",)
        ),
    )
