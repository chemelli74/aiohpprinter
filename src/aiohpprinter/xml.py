# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Convert HP EWS XML responses into plain nested dictionaries.

HP printers expose their embedded web server (EWS) data as namespaced XML
documents (``DevMgmt``/``ePrint``/``IoMgmt``). Different printer models,
firmware revisions and product generations emit different sets of elements
for the same document, so parsing here is intentionally tolerant: unknown or
missing elements are simply absent from the resulting dict rather than
raising, and callers look values up by path with :func:`get_path`.

The conversion follows the same shape as the well known ``xmltodict``
convention (attributes prefixed with ``@``, text content of a mixed element
under ``#text``), without requiring that dependency.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import ParseError

from defusedxml.ElementTree import fromstring

from .const import IGNORED_ROOT_KEYS
from .exceptions import HpPrinterParseError

if TYPE_CHECKING:
    from collections.abc import Mapping
    from xml.etree.ElementTree import Element


def parse_document(content: str) -> dict[str, Any]:
    """Parse a full EWS XML document into a dict keyed by its root tag.

    Namespace prefixes are stripped from every tag and attribute name, and
    schema/protocol bookkeeping keys (``xsi:schemaLocation``, ``Version``)
    are removed from the root element, mirroring what printer data consumers
    actually look at.
    """
    try:
        root = fromstring(content)
    except ParseError as ex:
        message = f"Could not parse printer response as XML: {ex}"
        raise HpPrinterParseError(message) from ex

    _strip_namespaces(root)
    document = {root.tag: _element_to_value(root)}
    _strip_ignored_root_keys(document)

    return document


def parse_json_document(content: str) -> dict[str, Any]:
    """Parse a JSON-encoded EWS response into the same dict shape.

    A small number of endpoints (observed on `/IoMgmt/Adapters`) answer with
    a `Content-Type: application/javascript` JSON body instead of XML, using
    the same element names as their XML counterparts. This lets the same
    path-based parsers read either shape.
    """
    try:
        document = json.loads(content)
    except json.JSONDecodeError as ex:
        message = f"Could not parse printer response as JSON: {ex}"
        raise HpPrinterParseError(message) from ex

    if not isinstance(document, dict):
        message = "Printer JSON response was not an object"
        raise HpPrinterParseError(message)

    _strip_ignored_root_keys(document)

    return document


def _strip_ignored_root_keys(document: dict[str, Any]) -> None:
    for root_value in document.values():
        if isinstance(root_value, dict):
            for ignored_key in IGNORED_ROOT_KEYS:
                root_value.pop(ignored_key, None)


def get_path(data: Mapping[str, Any] | None, path: str) -> Any:  # noqa: ANN401
    """Return the value found by walking a dot-separated path, or `None`.

    Missing intermediate elements, and paths that hit a list or scalar
    before they are exhausted, resolve to `None` instead of raising -
    printer firmware is free to omit optional elements entirely.
    """
    value: Any = data

    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)

    return value


def _strip_namespaces(element: Element) -> None:
    element.tag = _local_name(element.tag)

    for key in list(element.attrib):
        local_key = _local_name(key)
        if local_key != key:
            element.attrib[local_key] = element.attrib.pop(key)

    for child in element:
        _strip_namespaces(child)


def _local_name(qualified_name: str) -> str:
    if qualified_name.startswith("{"):
        return qualified_name.split("}", 1)[1]
    return qualified_name


def _element_to_value(element: Element) -> Any:  # noqa: ANN401
    children = list(element)
    text = (element.text or "").strip()
    attributes = {f"@{name}": value for name, value in element.attrib.items()}

    if not children:
        if attributes:
            return {**attributes, "#text": text} if text else attributes
        return text or None

    value: dict[str, Any] = dict(attributes)
    if text:
        value["#text"] = text

    for child in children:
        child_value = _element_to_value(child)

        if child.tag in value:
            existing = value[child.tag]
            if isinstance(existing, list):
                existing.append(child_value)
            else:
                value[child.tag] = [existing, child_value]
        else:
            value[child.tag] = child_value

    return value
