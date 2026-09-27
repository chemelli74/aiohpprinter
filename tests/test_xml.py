# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Tests for the XML/JSON-to-dict conversion layer."""

from __future__ import annotations

import pytest

from aiohpprinter.exceptions import HpPrinterParseError
from aiohpprinter.xml import get_path, parse_document, parse_json_document


def test_parse_document_strips_namespaces_from_tags_and_attributes() -> None:
    """Namespace prefixes are removed from both tags and attribute names."""
    content = (
        '<pudyn:ProductUsageDyn xmlns:pudyn="urn:example" xmlns:dd="urn:dd">'
        '<pudyn:PrinterSubunit dd:PEID="1">'
        "<dd:TotalImpressions>10</dd:TotalImpressions>"
        "</pudyn:PrinterSubunit>"
        "</pudyn:ProductUsageDyn>"
    )

    document = parse_document(content)

    assert get_path(document, "ProductUsageDyn.PrinterSubunit.@PEID") == "1"
    assert get_path(document, "ProductUsageDyn.PrinterSubunit.TotalImpressions") == "10"


def test_parse_document_strips_ignored_root_keys() -> None:
    """Schema/version bookkeeping on the root element is dropped."""
    content = (
        '<Root xmlns:xsi="urn:xsi" xsi:schemaLocation="urn:xsi thing.xsd">'
        "<Version>1</Version>"
        "<Data>value</Data>"
        "</Root>"
    )

    document = parse_document(content)

    assert "@schemaLocation" not in document["Root"]
    assert "Version" not in document["Root"]
    assert document["Root"]["Data"] == "value"


def test_parse_document_raises_on_malformed_xml() -> None:
    """Invalid XML raises a typed parse error, not a raw stdlib exception."""
    with pytest.raises(HpPrinterParseError):
        parse_document("<not><valid")


def test_parse_document_raises_on_entity_declaration() -> None:
    """A document with a forbidden DTD/entity raises a typed parse error.

    `defusedxml` rejects these with its own exception hierarchy
    (`DefusedXmlException`, a `ValueError` subclass), not `ParseError`.
    """
    content = (
        '<?xml version="1.0"?>'
        '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        "<foo>&xxe;</foo>"
    )

    with pytest.raises(HpPrinterParseError):
        parse_document(content)


def test_parse_document_element_with_attribute_and_text() -> None:
    """An element with both an attribute and text keeps both under `#text`."""
    document = parse_document('<Root><Value PEID="5">42</Value></Root>')

    assert document["Root"]["Value"] == {"@PEID": "5", "#text": "42"}


def test_parse_document_element_with_only_attribute() -> None:
    """An attribute-only, textless element has no `#text` key."""
    document = parse_document('<Root><Value PEID="5"/></Root>')

    assert document["Root"]["Value"] == {"@PEID": "5"}


def test_parse_document_empty_element_is_none() -> None:
    """A childless, attribute-less, textless element resolves to `None`."""
    document = parse_document("<Root><Value/></Root>")

    assert document["Root"]["Value"] is None


def test_parse_document_element_with_text_and_children() -> None:
    """Mixed content keeps both the text and the child elements."""
    document = parse_document("<Root>hello<Child>1</Child></Root>")

    assert document["Root"]["#text"] == "hello"
    assert document["Root"]["Child"] == "1"


def test_parse_document_repeated_tags_become_a_list() -> None:
    """Three or more repeated sibling tags all collect into one list."""
    content = "<Root><Item>1</Item><Item>2</Item><Item>3</Item></Root>"

    document = parse_document(content)

    assert document["Root"]["Item"] == ["1", "2", "3"]


def test_parse_json_document_strips_ignored_root_keys() -> None:
    """The JSON path applies the same root key stripping as the XML path."""
    content = '{"Adapters": {"Version": "1", "Adapter": []}}'

    document = parse_json_document(content)

    assert document == {"Adapters": {"Adapter": []}}


def test_parse_json_document_raises_on_invalid_json() -> None:
    """Invalid JSON raises a typed parse error."""
    with pytest.raises(HpPrinterParseError):
        parse_json_document("{not json")


def test_parse_json_document_raises_when_not_an_object() -> None:
    """A JSON document that isn't an object is rejected."""
    with pytest.raises(HpPrinterParseError):
        parse_json_document("[1, 2, 3]")


def test_get_path_returns_none_for_missing_intermediate_key() -> None:
    """A path through a key that does not exist resolves to `None`."""
    assert get_path({"a": {"b": "c"}}, "a.x.y") is None


def test_get_path_returns_none_when_data_is_none() -> None:
    """Looking up a path in `None` data resolves to `None`."""
    assert get_path(None, "a.b") is None


def test_get_path_returns_none_past_a_scalar() -> None:
    """A path that continues past a scalar value resolves to `None`."""
    assert get_path({"a": "scalar"}, "a.b") is None


def test_get_path_returns_none_past_a_list() -> None:
    """A path that continues past a list value resolves to `None`."""
    assert get_path({"a": ["x", "y"]}, "a.b") is None
