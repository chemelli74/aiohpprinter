# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser tests: fixture-driven regression suite plus targeted edge cases.

The fixture-driven tests in this file are what makes adding support for a
new printer model a matter of dropping XML files into
`tests/fixtures/<model>/` rather than writing new test functions - see
`discover_fixtures()` in `conftest.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from aiohpprinter.parsers import (
    parse_adapters,
    parse_consumables,
    parse_copy_usage,
    parse_device,
    parse_eprint,
    parse_fax_usage,
    parse_printer_usage,
    parse_scanner_usage,
    parse_status,
    parse_wifi,
)
from aiohpprinter.parsers.common import boolean, integer, number, text, timestamp
from aiohpprinter.xml import parse_document, parse_json_document
from tests.conftest import (
    discover_fixtures,
    load_document,
    load_expected,
    to_json_safe,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

FIXTURE_DIRS = discover_fixtures()

#: Golden keys backed by exactly one endpoint document each.
_SINGLE_DOCUMENT_PARSERS: dict[str, tuple[str, Callable[[dict[str, Any]], Any]]] = {
    "device": ("ProductConfigDyn.xml", parse_device),
    "status": ("ProductStatusDyn.xml", parse_status),
    "adapters": ("Adapters.xml", parse_adapters),
    "eprint": ("ePrintConfigDyn.xml", parse_eprint),
    "wifi": ("NetAppsSecureDyn.xml", parse_wifi),
    "printer_usage": ("ProductUsageDyn.xml", parse_printer_usage),
    "scanner_usage": ("ProductUsageDyn.xml", parse_scanner_usage),
    "copy_usage": ("ProductUsageDyn.xml", parse_copy_usage),
    "fax_usage": ("ProductUsageDyn.xml", parse_fax_usage),
}


def _parse_golden_key(fixture_dir: Path, key: str) -> Any:  # noqa: ANN401
    if key == "consumables":
        return parse_consumables(
            load_document(fixture_dir, "ConsumableConfigDyn.xml"),
            load_document(fixture_dir, "ProductUsageDyn.xml"),
        )

    filename, parser = _SINGLE_DOCUMENT_PARSERS[key]
    document = load_document(fixture_dir, filename)
    assert document is not None, (
        f"{fixture_dir.name}/expected.json references {key} but has no {filename}"
    )
    return parser(document)


def _golden_cases() -> list[tuple[Path, str]]:
    return [
        (fixture_dir, key)
        for fixture_dir in FIXTURE_DIRS
        for key in load_expected(fixture_dir)
    ]


_GOLDEN_CASES = _golden_cases()


@pytest.mark.parametrize(
    ("fixture_dir", "key"),
    _GOLDEN_CASES,
    ids=[f"{fixture_dir.name}-{key}" for fixture_dir, key in _GOLDEN_CASES],
)
def test_fixture_matches_expected(fixture_dir: Path, key: str) -> None:
    """A fixture's parsed value for `key` matches its golden `expected.json`."""
    expected = load_expected(fixture_dir)[key]

    actual = to_json_safe(_parse_golden_key(fixture_dir, key))

    assert actual == expected


@pytest.mark.parametrize("fixture_dir", FIXTURE_DIRS, ids=lambda p: p.name)
def test_fixture_endpoints_parse_without_error(fixture_dir: Path) -> None:
    """Every XML/JSON document present in a fixture parses without raising."""
    xml_files = list(fixture_dir.glob("*.xml"))
    json_files = [p for p in fixture_dir.glob("*.json") if p.name != "expected.json"]

    assert xml_files or json_files, f"{fixture_dir.name} has no fixture documents"

    for xml_path in xml_files:
        assert parse_document(xml_path.read_text())
    for json_path in json_files:
        assert parse_json_document(json_path.read_text())


def test_status_uses_first_entry_when_the_printer_reports_several() -> None:
    """Multiple `Status` entries: the overall category is the first one."""
    document = parse_document(
        "<ProductStatusDyn>"
        "<Status><StatusCategory>processing</StatusCategory></Status>"
        "<Status><StatusCategory>ready</StatusCategory></Status>"
        "</ProductStatusDyn>"
    )

    status = parse_status(document)

    assert status.device_status == "processing"


def test_status_missing_document_section_is_none() -> None:
    """A `ProductStatusDyn` document without a `Status` section is tolerated."""
    status = parse_status(parse_document("<ProductStatusDyn/>"))

    assert status.device_status is None


def test_consumables_merges_config_only_entry() -> None:
    """A consumable reported only by the config endpoint is still returned."""
    config = parse_document(
        "<ConsumableConfigDyn>"
        "<ConsumableInfo><ConsumableLabelCode>K</ConsumableLabelCode></ConsumableInfo>"
        "</ConsumableConfigDyn>"
    )

    consumables = parse_consumables(config, None)

    assert [c.consumable_id for c in consumables] == ["K"]
    assert consumables[0].marker_color is None


def test_consumables_merges_usage_only_entry() -> None:
    """A consumable reported only by the usage endpoint is still returned."""
    usage = parse_document(
        "<ProductUsageDyn><ConsumableSubunit>"
        "<Consumable><MarkerColor>Black</MarkerColor></Consumable>"
        "</ConsumableSubunit></ProductUsageDyn>"
    )

    consumables = parse_consumables(None, usage)

    assert [c.consumable_id for c in consumables] == ["K"]
    assert consumables[0].consumable_type is None


def test_consumables_falls_back_to_raw_marker_color_when_unmapped() -> None:
    """An unrecognized marker color is kept as-is instead of dropped."""
    usage = parse_document(
        "<ProductUsageDyn><ConsumableSubunit>"
        "<Consumable><MarkerColor>LightCyan</MarkerColor></Consumable>"
        "</ConsumableSubunit></ProductUsageDyn>"
    )

    consumables = parse_consumables(None, usage)

    assert [c.consumable_id for c in consumables] == ["LightCyan"]


def test_consumables_with_no_documents_is_empty() -> None:
    """Both consumable endpoints missing yields an empty list, not an error."""
    assert parse_consumables(None, None) == []


def test_consumables_skips_usage_item_without_marker_color() -> None:
    """A usage entry with no marker color has no way to identify it, and is skipped."""
    usage = parse_document(
        "<ProductUsageDyn><ConsumableSubunit>"
        "<Consumable><ConsumableState>ok</ConsumableState></Consumable>"
        "</ConsumableSubunit></ProductUsageDyn>"
    )

    assert parse_consumables(None, usage) == []


def test_consumables_skips_config_item_without_label_code() -> None:
    """A config entry with no label code has no way to identify it, and is skipped."""
    config = parse_document(
        "<ConsumableConfigDyn>"
        "<ConsumableInfo><ConsumableTypeEnum>ink</ConsumableTypeEnum></ConsumableInfo>"
        "</ConsumableConfigDyn>"
    )

    assert parse_consumables(config, None) == []


def test_consumables_skips_non_dict_config_entries() -> None:
    """A malformed, non-object `ConsumableInfo` entry is skipped, not raised."""
    config = {"ConsumableConfigDyn": {"ConsumableInfo": ["not-an-object"]}}

    assert parse_consumables(config, None) == []


def test_adapters_returns_empty_list_when_section_is_absent() -> None:
    """An `Adapters` document without any `Adapter` element yields `[]`."""
    document = parse_document("<Adapters/>")

    assert parse_adapters(document) == []


@pytest.mark.parametrize(
    ("ssid_prefix_element", "expected"),
    [
        pytest.param(
            "<SSIDPrefix>4449524543542d42332d485020</SSIDPrefix>",
            "DIRECT-B3-HP",
            id="hex",
        ),
        pytest.param("<SSIDPrefix>DIRECT-9020</SSIDPrefix>", "DIRECT-9020", id="plain"),
        pytest.param("<SSIDPrefix>00ff</SSIDPrefix>", "00ff", id="hex-not-printable"),
        pytest.param("", None, id="missing"),
    ],
)
def test_wifi_ssid_prefix_decoding(
    ssid_prefix_element: str, expected: str | None
) -> None:
    """A hex-encoded SSID prefix is decoded; anything else is kept as-is."""
    document = parse_document(
        "<NetAppsSecureDyn><WirelessDirectConfig>"
        f"{ssid_prefix_element}<ConnectionMethod>auto</ConnectionMethod>"
        "</WirelessDirectConfig></NetAppsSecureDyn>"
    )

    assert parse_wifi(document).ssid_prefix == expected


def test_eprint_reads_printer_id() -> None:
    """`PrinterID` is read when present; no captured model reports it yet."""
    document = parse_document(
        "<ePrintConfigDyn><PrinterID>ABC123</PrinterID></ePrintConfigDyn>"
    )

    assert parse_eprint(document).printer_id == "ABC123"


def test_text_unwraps_hash_text_from_attributed_element() -> None:
    """A `{"@PEID": ..., "#text": ...}` shape resolves to the text value."""
    assert text({"Value": {"@PEID": "1", "#text": "42"}}, "Value") == "42"


def test_text_returns_none_for_blank_string() -> None:
    """Whitespace-only text resolves to `None`, not an empty string."""
    assert text({"Value": "   "}, "Value") is None


def test_integer_returns_none_for_non_numeric_text() -> None:
    """Non-numeric text does not raise; it resolves to `None`."""
    assert integer({"Value": "not-a-number"}, "Value") is None


def test_number_returns_none_for_non_numeric_text() -> None:
    """Non-numeric text does not raise; it resolves to `None`."""
    assert number({"Value": "not-a-number"}, "Value") is None


def test_number_parses_float_text() -> None:
    """A decimal value parses to a float."""
    assert number({"Value": "3.5"}, "Value") == pytest.approx(3.5)


def test_boolean_is_case_insensitive() -> None:
    """Matching against `true_values` ignores case."""
    assert boolean({"Value": "TRUE"}, "Value", ("true",)) is True


def test_boolean_returns_false_for_non_matching_value() -> None:
    """A value not present in `true_values` resolves to `False`."""
    assert boolean({"Value": "false"}, "Value", ("true",)) is False


def test_boolean_returns_none_when_missing() -> None:
    """A missing value resolves to `None`, not `False`."""
    assert boolean({}, "Value", ("true",)) is None


def test_timestamp_returns_none_for_invalid_format() -> None:
    """An unparsable timestamp does not raise; it resolves to `None`."""
    assert timestamp({"Value": "not-a-date"}, "Value") is None
