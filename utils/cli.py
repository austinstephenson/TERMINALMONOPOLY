"""
Command-line interface definitions for Terminal Monopoly.

Both entry points (banker.py and player.py) build their parsers here so that
shared flags stay consistent and `--help` output is generated in one place.

Every flag has a modern `--flag` form and a legacy `-flag` alias (for example
`--local` and `-local`), so existing commands and scripts keep working.
"""

import argparse
import ipaddress
from typing import Sequence

MIN_PORT = 1024  # Same range the banker enforces when prompting for a port
MAX_PORT = 65535


def _base_parser(prog: str, description: str) -> argparse.ArgumentParser:
    """
    Create a parser containing the flags shared by banker.py and player.py.

    Parameters:
        prog (str): Program name shown in the usage line.
        description (str): Text shown at the top of the help screen.

    Returns: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument("--local", "-local", action="store_true",
                        help="play on localhost using port 33333 (no IP/port prompts)")
    parser.add_argument("--skipcalib", "-skipcalib", action="store_true",
                        help="skip screen calibration")
    return parser


def build_banker_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser for banker.py.

    Returns: argparse.ArgumentParser
    """
    parser = _base_parser("banker.py", "Run the Terminal Monopoly banker (game host).")
    parser.add_argument("--silent", "-silent", action="store_true",
                        help="hide output in the output areas (e.g. for tournament games)")
    parser.add_argument("--debtok", "-debtok", action="store_true",
                        help="allow players to go into debt")
    parser.add_argument("--stayopen", "-stayopen", action="store_true",
                        help="keep the receiver open after all players disconnect")
    parser.add_argument("test", nargs="?", type=int, default=None, metavar="TEST",
                        help="unit test number to run (see set_unittest in banker.py); "
                             "you are prompted for one if omitted")
    return parser


def build_player_parser() -> argparse.ArgumentParser:
    """
    Build the argument parser for player.py.

    Returns: argparse.ArgumentParser
    """
    parser = _base_parser("player.py", "Run a Terminal Monopoly player client.")
    parser.add_argument("--withnet", "-withnet", action="store_true",
                        help="enable network commands")
    parser.add_argument("--debug", "-debug", action="store_true",
                        help="enable debug mode (no network commands, prints a screen ruler)")
    parser.add_argument("--connect", "-connect", nargs=3, metavar=("NAME", "IP", "PORT"),
                        help="skip the prompts and connect straight to a banker; implies debug mode")
    return parser


def parse_banker_args(argv: Sequence[str] = None) -> argparse.Namespace:
    """
    Parse banker.py command-line arguments.

    Parameters: argv (Sequence[str]) - arguments to parse. Defaults to sys.argv[1:].

    Returns: argparse.Namespace with local, skipcalib, silent, debtok, stayopen, and test.
    """
    return build_banker_parser().parse_args(argv)


def parse_player_args(argv: Sequence[str] = None) -> argparse.Namespace:
    """
    Parse and validate player.py command-line arguments.

    Parameters: argv (Sequence[str]) - arguments to parse. Defaults to sys.argv[1:].

    Returns: argparse.Namespace with local, skipcalib, withnet, debug, and connect.
    Exits with a usage error if --connect is given an invalid IP address or port.
    """
    parser = build_player_parser()
    args = parser.parse_args(argv)
    if args.connect:
        _, ip, port = args.connect
        try:
            ipaddress.IPv4Address(ip)
        except ValueError:
            parser.error(f"--connect: invalid IP address '{ip}', use the format xxx.xxx.xxx.xxx")
        if not (port.isdigit() and MIN_PORT <= int(port) <= MAX_PORT):
            parser.error(f"--connect: invalid port '{port}', use a number from {MIN_PORT} to {MAX_PORT}")
    return args
