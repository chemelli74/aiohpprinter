# hp_color_laserjet_m255dw

**Provenance: real, user-contributed.** The endpoint responses were
downloaded by hand from the printer's EWS and shared as a zip archive,
then redacted with the sanitizer in `scripts/capture_fixture.py`. Only
the endpoints `aiohpprinter` reads are included (no `DiscoveryTree.xml`
resources).

Printer model: **HP Color LaserJet M255dw**

- `ConsumableConfigDyn.xml` (/DevMgmt/ConsumableConfigDyn.xml)
- `NetAppsSecureDyn.xml` (/DevMgmt/NetAppsSecureDyn.xml)
- `ProductConfigDyn.xml` (/DevMgmt/ProductConfigDyn.xml)
- `ProductStatusDyn.xml` (/DevMgmt/ProductStatusDyn.xml)
- `ProductUsageDyn.xml` (/DevMgmt/ProductUsageDyn.xml)
- `Adapters.xml` (/IoMgmt/Adapters)
- `ePrintConfigDyn.xml` (/ePrint/ePrintConfigDyn.xml)

## Sanitization

Identifying values (serial numbers, IDs, MAC/IP addresses, hostnames, SSIDs, e-mail addresses, credentials) were replaced with `REDACTED` by the capture script's sanitizer.
