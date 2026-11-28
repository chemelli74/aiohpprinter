# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/DevMgmt/ProductStatusDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import _DEVICE_STATUSES, HpPrinterStatus
from aiohpprinter.xml import get_path

from .common import as_list, first, first_text, text

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "ProductStatusDyn.Status"


def parse_status(document: dict[str, Any]) -> HpPrinterStatus:
    """Build status data from a parsed `ProductStatusDyn` document.

    A printer may report more than one `Status` entry (for example one per
    active job); the first one carries the overall `StatusCategory`.
    """
    entries = as_list(get_path(document, _ROOT_PATH))
    status = next(
        (
            entry
            for entry in entries
            if (text(entry, "StatusCategory") or "").lower() in _DEVICE_STATUSES
        ),
        first(entries),
    )

    device_status = text(status, "StatusCategory")

    return HpPrinterStatus(
        device_status=device_status.lower() if device_status else None,
        message=first_text(status, "LocString"),
    )
