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
    <img src="https://img.shields.io/pypi/v/aiohpprinter.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <a href="https://pypi.org/project/aiohpprinter/">
    <img src="https://img.shields.io/pypi/pyversions/aiohpprinter.svg?style=flat-square&amp;logo=python&amp;logoColor=fff" alt="Supported Python versions">
  </a>
  <img src="https://img.shields.io/pypi/l/aiohpprinter.svg?style=flat-square" alt="License">
</p>

---

**Source Code**: <a href="https://github.com/chemelli74/aiohpprinter" target="_blank">https://github.com/chemelli74/aiohpprinter </a>

---

Python library to get information from HP printers

## Installation

Install this via pip (or your favourite package manager):

`pip install aiohpprinter`

## Test

Test the library with:

`python library_test.py`

The script accepts command line arguments or a `library_test.json` config file:

```json
{
  "host": "<printer_ip_or_hostname>"
}
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
