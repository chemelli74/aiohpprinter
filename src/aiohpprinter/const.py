# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Constants for aiohpprinter."""

import logging

from aiohttp import ClientTimeout

_LOGGER = logging.getLogger(__package__)

DEFAULT_PORT = 80
DEFAULT_TIMEOUT = ClientTimeout(total=10)

# HP embedded web server (EWS) DevMgmt/ePrint/IoMgmt endpoints. These are the
# same URIs used by the upstream ha-hpprinter integration.
ENDPOINT_PRODUCT_STATUS = "/DevMgmt/ProductStatusDyn.xml"
ENDPOINT_PRODUCT_CONFIG = "/DevMgmt/ProductConfigDyn.xml"
ENDPOINT_CONSUMABLE_CONFIG = "/DevMgmt/ConsumableConfigDyn.xml"
ENDPOINT_PRODUCT_USAGE = "/DevMgmt/ProductUsageDyn.xml"
ENDPOINT_ADAPTERS = "/IoMgmt/Adapters"
ENDPOINT_EPRINT_CONFIG = "/ePrint/ePrintConfigDyn.xml"
ENDPOINT_NET_APPS_SECURE = "/DevMgmt/NetAppsSecureDyn.xml"

# A small number of endpoints (observed on `/IoMgmt/Adapters`) answer with a
# JSON body instead of XML, using either of these content types.
JSON_CONTENT_TYPES = frozenset({"application/javascript", "application/json"})

# Keys present on every response's root element that carry protocol/schema
# metadata rather than printer data, dropped once parsed.
IGNORED_ROOT_KEYS = ("@schemaLocation", "Version")

MARKER_COLOR_TO_LABEL_CODE = {
    "Cyan": "C",
    "Yellow": "Y",
    "Magenta": "M",
    "CyanMagentaYellow": "CMY",
    "Black": "K",
}
