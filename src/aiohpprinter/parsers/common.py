# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Typed field extraction helpers shared by the per-endpoint parsers.

Every helper resolves a dotted path (see :func:`aiohpprinter.xml.get_path`)
against a parsed document and converts it to the requested type, returning
`None` for anything missing or that fails to convert - printer firmware
frequently omits optional elements, and that must never break parsing.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from aiohpprinter.xml import get_path

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


def text(data: Mapping[str, Any] | None, path: str) -> str | None:
    """Return the string found at `path`, or `None` if missing/blank.

    Some elements carry a `PEID` (parameter ID) attribute on some printer
    models/firmware and not others, which changes how the XML layer
    represents them: a bare value versus a `{"@PEID": ..., "#text": ...}`
    dict. Both shapes resolve to the same text here so a parser field does
    not need to special-case attribute presence.
    """
    value = get_path(data, path)

    if isinstance(value, dict):
        value = value.get("#text")

    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None

    return None


def integer(data: Mapping[str, Any] | None, path: str) -> int | None:
    """Return the integer found at `path`, or `None` if missing/invalid."""
    value = text(data, path)

    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        return None


def number(data: Mapping[str, Any] | None, path: str) -> float | None:
    """Return the float found at `path`, or `None` if missing/invalid."""
    value = text(data, path)

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def boolean(
    data: Mapping[str, Any] | None,
    path: str,
    true_values: tuple[str, ...],
) -> bool | None:
    """Return whether the value at `path` matches one of `true_values`."""
    value = text(data, path)

    if value is None:
        return None

    return value.lower() in true_values


def timestamp(data: Mapping[str, Any] | None, path: str) -> datetime | None:
    """Return the ISO-8601 timestamp found at `path`, or `None`."""
    value = text(data, path)

    if value is None:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None
