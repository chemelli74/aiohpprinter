# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Constants for HP printers."""

import logging

from aiohttp import ClientTimeout

_LOGGER = logging.getLogger(__package__)

DEFAULT_PORT = 80
DEFAULT_TIMEOUT = ClientTimeout(10)
