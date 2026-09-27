# Copyright 2026 Simone Chemelli and contributors
# SPDX-License-Identifier: Apache-2.0

"""Manual test script for the aiohpprinter library."""

import asyncio
import dataclasses
import json
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

from aiohttp import ClientSession

from aiohpprinter import HpPrinter, HpPrinterError


def get_arguments() -> tuple[ArgumentParser, Namespace]:
    """Parse command line arguments, optionally seeded from a JSON config file."""
    parser = ArgumentParser(description="aiohpprinter library test")
    parser.add_argument("--host", "-H", type=str, help="Printer hostname or IP")
    parser.add_argument(
        "--port",
        "-P",
        type=int,
        default=None,
        help="EWS port (default: 443 with --ssl, else 80)",
    )
    parser.add_argument("--ssl", action="store_true", help="Use HTTPS for the EWS")
    parser.add_argument(
        "--configfile",
        "-cf",
        type=str,
        help="Load options from a JSON config file. "
        "Command line options override those in the file.",
    )

    arguments = parser.parse_args()
    if arguments.configfile and Path(arguments.configfile).exists():
        with Path(arguments.configfile).open(encoding="utf-8") as config:
            arguments = parser.parse_args(
                namespace=Namespace(**json.loads(config.read())),
            )

    return parser, arguments


async def main() -> None:
    """Run the manual test flow against a real printer."""
    parser, args = get_arguments()

    if not args.host:
        print("You have to specify a printer host")
        parser.print_help()
        sys.exit(1)

    port = args.port if args.port is not None else (443 if args.ssl else 80)
    print(f"Connecting to {args.host}:{port}")
    session = ClientSession()

    try:
        async with HpPrinter(
            args.host, session=session, port=port, ssl=args.ssl
        ) as printer:
            data = await printer.update()

            print("-" * 20)
            print(f"{'Online:':>24} {data.online}")

            if data.device:
                print(f"{'Model:':>24} {data.device.make_and_model}")
                print(f"{'Serial number:':>24} {data.device.serial_number}")

            if data.status:
                print(f"{'Status:':>24} {data.status.device_status}")

            for consumable in data.consumables:
                print("-" * 20)
                print(f"{'Consumable:':>24} {consumable.consumable_id}")
                print(f"{'Type:':>24} {consumable.consumable_type}")
                level = consumable.percentage_level_remaining
                print(f"{'Level remaining:':>24} {level}")

            if data.printer_usage:
                print("-" * 20)
                total = data.printer_usage.total_impressions
                print(f"{'Total impressions:':>24} {total}")

            print(json.dumps(dataclasses.asdict(data), default=str, indent=2))
    except HpPrinterError as ex:
        print(f"Failed to reach printer: {ex}")
        sys.exit(1)
    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(main())
