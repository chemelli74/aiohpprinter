# hp_laserjet_200_m251nw

**Provenance: real, captured.**

`ProductUsageDyn.xml` is a real `/DevMgmt/ProductUsageDyn.xml` response from
an **HP LaserJet 200 color M251nw**, posted publicly by user `jcollas` as a
[GitHub issue attachment](https://github.com/elad-bar/ha-hpprinter/files/3828478/ProductUsageDyn.txt)
on [`ha-hpprinter` issue #1](https://github.com/elad-bar/ha-hpprinter/issues/1)
(2019-11-10), while helping the maintainer debug a parsing crash. The model
is stated directly in that issue thread by the user who posted the file.

Being a color laser, print-only model, its shape differs from the
multifunction fixtures: no `ScannerEngineSubunit`,
`CopyApplicationSubunit` or `FaxApplicationSubunit`, toner consumables
identified only by `MarkerColor` (no separate `ConsumableConfigDyn.xml`
capture exists for this model), and richer per-consumable usage data
(`PreviousCartridgeData`, `A4EquivalentImpressions`, media-size breakdowns)
that the current parsers don't read - useful as a regression fixture if
support for those fields is ever added.

## Sanitization

None was required. The file contains only aggregate usage counters and
consumable telemetry - no serial numbers, MAC addresses, hostnames, IP
addresses or user-identifying data. It is included byte-for-byte as posted.
