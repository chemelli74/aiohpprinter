# aiohpprinter

<p align="center">
  <a href="https://github.com/chemelli74/aiohpprinter/actions/workflows/ci.yml?query=branch%3Amain">
    <img src="https://img.shields.io/github/actions/workflow/status/chemelli74/aiohpprinter/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://codecov.io/gh/chemelli74/aiohpprinter">
    <img src="https://img.shields.io/codecov/c/github/chemelli74/aiohpprinter.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://docs.astral.sh/uv/">
    <img src="https://img.shields.io/badge/packaging-uv-2A5BFF?style=flat-square" alt="uv">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://pypi.org/project/prek/">
    <img src="https://img.shields.io/badge/prek-enabled-brightgreen?style=flat-square" alt="prek">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/aiohpprinter/">
    <img src="https://img.shields.io/pypi/v/aiohpprinter.svg?logo=python&logoColor=fff&style=flat-square&cacheSeconds=300" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/aiohpprinter/">
    <img src="https://img.shields.io/pypi/pyversions/aiohpprinter.svg?style=flat-square&amp;logo=python&amp;logoColor=fff&amp;cacheSeconds=300" alt="Supported Python versions">
  </a>
  <img src="https://img.shields.io/pypi/l/aiohpprinter.svg?style=flat-square&cacheSeconds=300" alt="License">
</p>

---

**Source Code**: <a href="https://github.com/chemelli74/aiohpprinter" target="_blank">https://github.com/chemelli74/aiohpprinter </a>

---

Python library to get information from HP printers

`aiohpprinter` talks directly to an HP printer's embedded web server (EWS) -
the same `/DevMgmt/*.xml`, `/ePrint/*.xml` and `/IoMgmt/*` endpoints the
[`ha-hpprinter`](https://github.com/elad-bar/ha-hpprinter) Home Assistant
integration uses - and exposes the result as typed, async Python instead of
raw XML. It has no Home Assistant dependency and can be used from any async
Python application.

## Installation

Install this via pip (or your favourite package manager):

`pip install aiohpprinter`

## Basic usage

```python
import asyncio

from aiohpprinter import HpPrinter


async def main() -> None:
    async with HpPrinter("192.168.1.100") as printer:
        data = await printer.update()

        print(data.online)
        if data.device:
            print(data.device.make_and_model)
        for consumable in data.consumables:
            print(consumable.consumable_id, consumable.percentage_level_remaining)


asyncio.run(main())
```

`update()` is the one-call aggregate: it fetches every endpoint the printer
answers and returns an `HpPrinterData` snapshot. Each endpoint is also
available individually - `printer.device()`, `printer.status()`,
`printer.consumables()`, `printer.printer_usage()`, `printer.scanner_usage()`,
`printer.copy_usage()`, `printer.fax_usage()`, `printer.adapters()`,
`printer.eprint()`, `printer.wifi()` - for callers that only need one piece
of data, or that want failures raised instead of absorbed (see
**Exception handling** below).

## Session handling

`HpPrinter` accepts an optional `session: aiohttp.ClientSession`:

- **No session given**: `HpPrinter` creates its own `aiohttp.ClientSession`
  when entering `async with`, and closes it automatically on exit (or when
  `close()` is called explicitly). Use this for a standalone script.
- **Session injected**: the caller owns that session and is responsible for
  closing it - `HpPrinter` never closes a session it did not create. This is
  the recommended mode for an application such as Home Assistant that
  manages one shared session and its connection pooling itself.

```python
import aiohttp

async with aiohttp.ClientSession() as session:
    async with HpPrinter("192.168.1.100", session=session) as printer:
        device = await printer.device()

    # `session` is still open here; `printer`'s own state was released.
```

## Supported HP functionality

| Data                              | Endpoint                           | Notes                                           |
| --------------------------------- | ---------------------------------- | ----------------------------------------------- |
| Device identity                   | `/DevMgmt/ProductConfigDyn.xml`    | Model, serial number, manufacturer              |
| Status                            | `/DevMgmt/ProductStatusDyn.xml`    | Used as the "is the printer reachable" check    |
| Consumables (ink/toner/printhead) | `/DevMgmt/ConsumableConfigDyn.xml` | Life state, warranty, capacity                  |
| Consumable usage                  | `/DevMgmt/ProductUsageDyn.xml`     | Merged into the same consumable, by label code  |
| Printer engine usage              | `/DevMgmt/ProductUsageDyn.xml`     | Page counters                                   |
| Scanner engine usage              | `/DevMgmt/ProductUsageDyn.xml`     | Page counters                                   |
| Copy application usage            | `/DevMgmt/ProductUsageDyn.xml`     | Page counters                                   |
| Fax application usage             | `/DevMgmt/ProductUsageDyn.xml`     | Page counters                                   |
| Network adapters                  | `/IoMgmt/Adapters`                 | May reply as JSON instead of XML on some models |
| HP ePrint / cloud printing        | `/ePrint/ePrintConfigDyn.xml`      | Registration and cloud services state           |
| Wireless Direct                   | `/DevMgmt/NetAppsSecureDyn.xml`    | SSID prefix, connection method                  |

Only the status endpoint is treated as required (it is what `is_online()`
and `update()` use to decide whether the printer is reachable at all).
Every other endpoint is optional: not every HP printer supports scanning,
copying, faxing, cloud printing or Wireless Direct, and `update()` leaves
the corresponding field `None` (or an empty list) instead of failing when
one is missing.

## Exception handling

```text
HpPrinterError
├── HpPrinterConnectionError   # network/transport failure
├── HpPrinterTimeoutError      # request exceeded the client timeout
├── HpPrinterHttpError         # non-2xx HTTP status (`.status` holds it)
├── HpPrinterParseError        # response body was not valid XML/JSON
└── HpPrinterUnsupportedError  # reserved for a required feature genuinely absent
```

The single-endpoint methods (`device()`, `status()`, `consumables()`, ...)
raise these normally, so a caller that wants to distinguish "printer is
unreachable" from "printer sent garbage" can catch the specific subclass it
cares about, or `HpPrinterError` to catch anything.

`update()` and `is_online()` are the exception to that: they are explicitly
designed to tolerate a printer that only partially answers (see **Supported
HP functionality** above), so they catch every `HpPrinterError` from the
optional endpoints internally and never raise for that reason. `update()`
still lets a failure while checking `is_online()` be represented as
`online=False` rather than an exception, since that is the question it
exists to answer.

## Adding a New Printer Model

`aiohpprinter`'s test suite is fixture-driven: every directory under
`tests/fixtures/` is picked up automatically by both the parser suite
(`tests/test_parsers.py`) and an end-to-end `update()` test that serves the
fixture's files from a local HTTP server (`test_update_fixture` in
`tests/test_client.py`). No new test function is required.

1. Capture the printer with the fixture script, giving its IP address or
   hostname:

   ```shell
   python scripts/capture_fixture.py 192.168.1.100
   ```

   The model name, and so the fixture directory, is taken from the
   printer's `ProductConfigDyn.xml`: when it only reports its family
   (`MakeAndModel` "HP OfficeJet Pro 9020 series"), the variant from
   `SKUIdentifier` ("9022e") replaces the series number. Pass
   `--model "..."` to override it.

   This creates e.g. `tests/fixtures/hp_officejet_pro_9022e/` with:
   - every endpoint `aiohpprinter` reads (`ProductStatusDyn.xml` is
     required; any other endpoint answering 404 is skipped, since that
     model doesn't support that feature). `Adapters` is saved as
     `Adapters.json` when the printer answers it as JSON;
   - every other resource the printer lists in `/DevMgmt/DiscoveryTree.xml`
     (pass `--no-discovery` to skip these);
   - `expected.json`, generated from what the current parsers return;
   - a `README.md` recording the fixture's provenance.

   Serial numbers, IDs, MAC/IP addresses, hostnames, SSIDs, e-mail
   addresses and credentials are replaced with `REDACTED`. Use `--port` /
   `--ssl` for a non-default EWS, and `--force` to recapture over an
   existing directory.

2. Review the captured files for anything identifying the redaction
   missed, and check `expected.json`: it records what the parsers return
   today, so a wrong or missing value there is a parser bug to fix, not a
   value to keep.
3. Fix the relevant parser in `src/aiohpprinter/parsers/` if a field is
   missing or wrong, correct `expected.json` to match, then run the suite:
   `uv run pytest` (or `uv run pytest -k <model>` for just the new fixture).

## Known limitations

- Full captures (every endpoint `aiohpprinter` reads plus every
  `DiscoveryTree.xml` resource) exist for two models: HP OfficeJet Pro
  9022e and HP ENVY Photo 7830 All-in-One Printer. An HP Color LaserJet
  M255dw is covered by the endpoints `aiohpprinter` reads only, and an
  HP LaserJet 200 color M251nw by `ProductUsageDyn.xml` only. None of
  them reports an ePrint `PrinterID`, so that field is only covered by a
  unit test. If you have another printer, contributing a capture per
  **Adding a New Printer Model** above is very welcome.
- A field is looked up at one fixed XML path per printer generation
  (tolerant of a `PEID` attribute appearing or not, see
  `aiohpprinter.parsers.common.text`), but not of a field moving to a
  different element entirely on some model; that would need a fixture
  demonstrating the variation and a parser update.
- Fax usage has no real-world fixture with non-zero counters: both full
  captures report a `FaxApplicationSubunit` with every value at `0`.

## Manual testing against a real printer

`library_test.py` connects to a real printer and prints an `update()`
snapshot:

```shell
python library_test.py --host 192.168.1.100
```

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- readme: contributors -start -->
<table>
	<tbody>
		<tr>
            <td align="center">
                <a href="https://github.com/chemelli74">
                    <img src="https://avatars.githubusercontent.com/u/57354320?v=4" width="100;" alt="chemelli74"/>
                    <br />
                    <sub><b>Simone Chemelli</b></sub>
                </a>
            </td>
		</tr>
	<tbody>
</table>
<!-- readme: contributors -end -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Copier](https://copier.readthedocs.io/) and the
[browniebroke/pypackage-template](https://github.com/browniebroke/pypackage-template)
project template.
