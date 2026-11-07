# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/DevMgmt/ProductLogsDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpJob, HpLogEvent, HpProductLogs
from aiohpprinter.xml import get_path

from .common import as_list, integer, text, timestamp

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "ProductLogsDyn"


def parse_logs(document: dict[str, Any]) -> HpProductLogs:
    """Build the event, error and job logs from a `ProductLogsDyn` document.

    Events are sorted newest first, by sequence number.
    """
    logs = get_path(document, _ROOT_PATH)

    events = [
        _parse_event(item)
        for item in as_list(get_path(logs, "EventLog.Event"))
        if isinstance(item, dict)
    ]
    events.sort(key=lambda event: event.sequence_number or 0, reverse=True)

    return HpProductLogs(
        events=events,
        error_log=text(logs, "ErrorLog"),
        jobs=[
            _parse_job(item)
            for item in as_list(get_path(logs, "ColorUsageJobLog.JobList.JobEntry"))
            if isinstance(item, dict)
        ],
    )


def _parse_event(item: dict[str, Any]) -> HpLogEvent:
    return HpLogEvent(
        sequence_number=integer(item, "SequenceNumber"),
        event_code=text(item, "EventCode"),
        total_impressions=integer(item, "TotalImpressions"),
    )


def _parse_job(item: dict[str, Any]) -> HpJob:
    return HpJob(
        application_id=text(item, "DriverJobApplicationID"),
        user_id=text(item, "DriverJobUserID"),
        name=text(item, "DriverJobName"),
        monochrome_impressions=integer(item, "MonochromeImpressions"),
        color_impressions=integer(item, "ColorImpressions"),
        total_impressions=integer(item, "TotalImpressions"),
        submitted_at=timestamp(item, "DriverJobDateTime"),
    )
