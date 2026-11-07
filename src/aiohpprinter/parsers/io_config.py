# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Parser for the ``/DevMgmt/IOConfigDyn.xml`` endpoint."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiohpprinter.models import HpIOConfig
from aiohpprinter.xml import get_path

from .common import as_list, first, integer, text

if TYPE_CHECKING:
    from typing import Any

_ROOT_PATH = "IOConfigDyn.IOAdaptorConfig"


def parse_io_config(document: dict[str, Any]) -> HpIOConfig:
    """Build network adaptor data from an `IOConfigDyn` document.

    One `IOAdaptorConfig` is reported per port (USB included); only the one
    carrying a `NetworkAdaptorConfig` describes the network connection.
    """
    adaptor = next(
        (
            item
            for item in as_list(get_path(document, _ROOT_PATH))
            if isinstance(item, dict) and "NetworkAdaptorConfig" in item
        ),
        None,
    )
    network = get_path(adaptor, "NetworkAdaptorConfig")
    statistics = get_path(adaptor, "NetworkStatistics")

    return HpIOConfig(
        connectivity_port_type=text(adaptor, "DeviceConnectivityPortType"),
        # The first IP version entry is IPv4.
        network_status=text(
            first(get_path(network, "IPVersionConfig")), "NetworkStatus"
        ),
        speed_duplex_negotiation_mode=text(network, "SpeedDuplexNegotiationMode"),
        total_packets_received=integer(statistics, "TotalPacketsReceived"),
        total_packets_transmitted=integer(statistics, "TotalPacketsTransmitted"),
        bad_packets_received=integer(statistics, "BadPacketsReceived"),
        framing_errors_received=integer(statistics, "FramingErrorsReceived"),
        transmit_collisions=integer(statistics, "TransmitCollisions"),
        transmit_late_collisions=integer(statistics, "TransmitLateCollisions"),
        unsendable_packets=integer(statistics, "UnsendablePackets"),
    )
