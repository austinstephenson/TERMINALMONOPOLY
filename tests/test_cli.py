"""
Unit tests for utils/cli.py, the argparse definitions for banker.py and player.py.

Run from the repository root with: python -m unittest tests.test_cli -v
"""

import contextlib
import io
import unittest

from utils import cli


def parse_expecting_error(parse, argv):
    """Run a parse function that should call sys.exit, silencing argparse's stderr output."""
    with contextlib.redirect_stderr(io.StringIO()):
        with contextlib.suppress(SystemExit):
            parse(argv)
            return False
    return True


class BankerArgsTests(unittest.TestCase):
    """Tests for banker.py arguments."""

    def test_defaults(self):
        """No arguments leaves every flag off and prompts for a test number."""
        args = cli.parse_banker_args([])
        self.assertFalse(any([args.local, args.skipcalib, args.silent, args.debtok, args.stayopen]))
        self.assertIsNone(args.test)

    def test_new_style_flags(self):
        """Double-dash flags are recognised."""
        args = cli.parse_banker_args(["--local", "--silent", "--debtok", "--stayopen", "--skipcalib"])
        self.assertTrue(all([args.local, args.silent, args.debtok, args.stayopen, args.skipcalib]))

    def test_legacy_single_dash_flags(self):
        """The original single-dash flags still work."""
        args = cli.parse_banker_args(["-local", "-silent", "-debtok", "-stayopen", "-skipcalib"])
        self.assertTrue(all([args.local, args.silent, args.debtok, args.stayopen, args.skipcalib]))

    def test_test_number_anywhere(self):
        """The unit test number is parsed whether it comes first or after flags."""
        self.assertEqual(cli.parse_banker_args(["3"]).test, 3)
        self.assertEqual(cli.parse_banker_args(["--local", "5"]).test, 5)

    def test_custom_test_number(self):
        """-1 selects the 'create your own test' option."""
        self.assertEqual(cli.parse_banker_args(["-1"]).test, -1)

    def test_non_numeric_test_rejected(self):
        """A non-numeric test number is a usage error."""
        self.assertTrue(parse_expecting_error(cli.parse_banker_args, ["abc"]))

    def test_unknown_flag_rejected(self):
        """Unknown flags are a usage error instead of being silently ignored."""
        self.assertTrue(parse_expecting_error(cli.parse_banker_args, ["--nope"]))


class PlayerArgsTests(unittest.TestCase):
    """Tests for player.py arguments."""

    def test_defaults(self):
        """No arguments leaves every flag off."""
        args = cli.parse_player_args([])
        self.assertFalse(any([args.local, args.skipcalib, args.withnet, args.debug]))
        self.assertIsNone(args.connect)

    def test_flags_both_styles(self):
        """New and legacy spellings both work."""
        for argv in (["--local", "--withnet", "--debug", "--skipcalib"],
                     ["-local", "-withnet", "-debug", "-skipcalib"]):
            args = cli.parse_player_args(argv)
            self.assertTrue(all([args.local, args.withnet, args.debug, args.skipcalib]))

    def test_connect(self):
        """--connect takes a name, IP and port."""
        args = cli.parse_player_args(["--connect", "Bob", "192.168.1.5", "3131"])
        self.assertEqual(args.connect, ["Bob", "192.168.1.5", "3131"])

    def test_connect_invalid_ip(self):
        """An invalid IP address is rejected."""
        for ip in ("999.1.1.1", "1.2.3", "abc"):
            self.assertTrue(parse_expecting_error(cli.parse_player_args, ["--connect", "Bob", ip, "3131"]), ip)

    def test_connect_invalid_port(self):
        """Ports outside 1024-65535 or non-numeric are rejected."""
        for port in ("80", "70000", "abc"):
            self.assertTrue(parse_expecting_error(cli.parse_player_args, ["--connect", "Bob", "1.2.3.4", port]), port)

    def test_connect_needs_three_values(self):
        """--connect with missing values is a usage error."""
        self.assertTrue(parse_expecting_error(cli.parse_player_args, ["--connect", "Bob", "1.2.3.4"]))


if __name__ == "__main__":
    unittest.main()
