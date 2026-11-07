# Changelog

## v3.2.0 (2026-11-07)

### Features

- Add network adaptor statistics endpoint ([`3bee2a8`](https://github.com/chemelli74/aiohpprinter/commit/3bee2a89adde75848d664a01b97f083041fefe5f))


### Build system

- Anchor the uv version lookup in pyproject.toml ([`910f14c`](https://github.com/chemelli74/aiohpprinter/commit/910f14c11f337c87f3813d65a5cfc6c22bd21cbb))
- Make cleanup scripts safer to run ([`98262e1`](https://github.com/chemelli74/aiohpprinter/commit/98262e167b42a6e0d162de2706220d9385de21cb))
- Stop grouping python dependency bumps ([`6c6d481`](https://github.com/chemelli74/aiohpprinter/commit/6c6d4813ebcb0b29330f86e6186e0ec8f0b48b39))


## v3.1.1 (2026-11-02)

### Bug fixes

- Update dependency yarl to >=1.25.1 ([`49ccf6d`](https://github.com/chemelli74/aiohpprinter/commit/49ccf6dadc600f5e9c6fc9f88151069e251220f3))


### Refactoring

- Build printer urls with yarl ([`33e60ba`](https://github.com/chemelli74/aiohpprinter/commit/33e60ba15127be8d38601fc65ffb1d0367e95c26))
- Use orjson for json encoding and decoding ([`2747cdd`](https://github.com/chemelli74/aiohpprinter/commit/2747cddd70c3de3e5f6cbf71b26359a978f58952))


### Documentation

- Contrib-readme-action has updated readme ([`4105761`](https://github.com/chemelli74/aiohpprinter/commit/4105761e249d1762c0a12096f1e694393281af86))
- Contrib-readme-action has updated readme ([`d35f901`](https://github.com/chemelli74/aiohpprinter/commit/d35f901ea80a1a5b550557e45dfa03e529dc086c))


### Testing

- Add hp envy 4524 fixtures ([`a370e47`](https://github.com/chemelli74/aiohpprinter/commit/a370e47c687e7a08b42771032f4f7bf2f270d173))
- Add hp officejet pro 8035e fixtures ([`49cc85c`](https://github.com/chemelli74/aiohpprinter/commit/49cc85c052a25671b6b4124fd119dbd8ce6e9d3a))
- Add hp color laser mfp 178nw fixtures ([`bcf8b43`](https://github.com/chemelli74/aiohpprinter/commit/bcf8b435019356c88c721869ccd12773584f5442))


### Build system

- Target python 3.12 in pyupgrade ([`632f78a`](https://github.com/chemelli74/aiohpprinter/commit/632f78a357800c8024ca4aa49dfb87250d2a553e))


## v3.1.0 (2026-10-23)

### Features

- Fully support https and self-signed certs ([`39934d0`](https://github.com/chemelli74/aiohpprinter/commit/39934d0ec024e62c5c0aa6bca40ed13138679eda))


## v3.0.0 (2026-10-20)

### Refactoring

- Require an injected aiohttp session ([`d6d629c`](https://github.com/chemelli74/aiohpprinter/commit/d6d629cf8fae825801307d4fd82cb97b06dea922))


### Testing

- Add hp color laserjet mfp m476dw fixtures ([`5972dc9`](https://github.com/chemelli74/aiohpprinter/commit/5972dc9ad656989d238e81e3a38ffcaeb55dee5f))


## v2.0.0 (2026-10-19)

### Refactoring

- Move hpprinterdata.consumables to dict ([`837d249`](https://github.com/chemelli74/aiohpprinter/commit/837d249bb6bdb933c8477998aa003f1dc28f351d))


## v1.1.0 (2026-10-19)

### Features

- Add snake_case status and consumable color enums ([`bc8fb9d`](https://github.com/chemelli74/aiohpprinter/commit/bc8fb9dea7d876511d0a0c446d4242306e7ba165))


### Build system

- Stop bumping the python minor/major version ([`58edf7e`](https://github.com/chemelli74/aiohpprinter/commit/58edf7e4636c4faa8305a553930fda3c8662fc83))
- Bump multidict from 6.9.0 to 6.9.1 in the uv group across 1 directory ([`46cd85e`](https://github.com/chemelli74/aiohpprinter/commit/46cd85eb88be6c3acc961fef6e1a98d276291fdb))


## v1.0.1 (2026-10-18)

### Bug fixes

- Update python dependencies ([`b2f2d12`](https://github.com/chemelli74/aiohpprinter/commit/b2f2d128c577589629562ff97925bf8b0d4d7d50))


### Build system

- Update devcontainer, vscode and renovate ([`fe5d7ce`](https://github.com/chemelli74/aiohpprinter/commit/fe5d7ce93ab8796187a3fccb55edf16afe508fc6))
- Always use the repository .venv for uv ([`32ddfaf`](https://github.com/chemelli74/aiohpprinter/commit/32ddfafd7876446a279c95667fa47fb696a21247))
- Drop redundant anyio and mypy dev deps ([`bf39bf5`](https://github.com/chemelli74/aiohpprinter/commit/bf39bf5f895f1aac1b877bfdd456c4e3d1e7f925))
- Move coverage config to pyproject ([`caff4e4`](https://github.com/chemelli74/aiohpprinter/commit/caff4e456ec486cefda762b0bb89793da99b8471))
- Align vs code terminal env and contributing guide ([`6a121bf`](https://github.com/chemelli74/aiohpprinter/commit/6a121bfee391c3bc24bbbedbf422ccdb6e29a66e))
- Remove unused ruff ignores ([`269f09d`](https://github.com/chemelli74/aiohpprinter/commit/269f09dd2b0a151b05d8874a3fc6828033598b60))
- Pin runtime deps for mypy pre-commit hook ([`648c572`](https://github.com/chemelli74/aiohpprinter/commit/648c57207054f2c698c4984aa64c100b4fad6bf2))
- Replace unmaintained labels tool ([`1e852e3`](https://github.com/chemelli74/aiohpprinter/commit/1e852e30e236aecf4362e79d62677248733f188d))
- Bust stale cache on pypi badges ([`51d437d`](https://github.com/chemelli74/aiohpprinter/commit/51d437d37a41ed9f720a9f567ee6aa93af3599f7))
- Codecov coverage ([`df7ebe2`](https://github.com/chemelli74/aiohpprinter/commit/df7ebe2fd7d8eb21e453e9dcb2196d5adf89ef24))


### Testing

- Update envy photo 7830 fixtures ([`0320c17`](https://github.com/chemelli74/aiohpprinter/commit/0320c176916da0af2711713199692acf29daad3d))


## v1.0.0 (2026-09-27)

### Features

- Implement the aiohpprinter ews client, parsers, and models ([`e38ddb0`](https://github.com/chemelli74/aiohpprinter/commit/e38ddb0d40e77be132a751277bebc19ada02da7c))


### Documentation

- Contrib-readme-action has updated readme ([`6cd2bd6`](https://github.com/chemelli74/aiohpprinter/commit/6cd2bd65127756243dead5390db4dd7a129734af))
