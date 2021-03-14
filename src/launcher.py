"""
WalBot launcher
"""

import argparse
import importlib
import sys

from src import const


class Launcher:
    """This class parses provided command line options and dispatches execution depending on them."""

    def __init__(self):
        self._parser = argparse.ArgumentParser(description='WalBot', formatter_class=argparse.RawTextHelpFormatter)
        subparsers = self._parser.add_subparsers(dest="action")
        subparsers = {
            cmd: subparsers.add_parser(
                cmd, help=getattr(self, cmd).__doc__, formatter_class=argparse.RawTextHelpFormatter)
            for cmd in list(filter(lambda _: not _.startswith('_'), dir(self)))
        }
        subparsers["start"].add_argument(
            "--autoupdate", action="store_true",
            help="Start autoupdate process for bot")
        # Start & suspend
        for option in ("start", "restart", "suspend"):
            subparsers[option].add_argument(
                "--fast_start", action="store_true",
                help=("Make bot start faster by disabling some optional checks:\n"
                      "- Disable Markov model check on start\n"
                      ))
            subparsers[option].add_argument(
                "--patch", action="store_true",
                help="Call script for patching config files before starting the bot")
            if sys.platform in ("linux", "darwin"):
                subparsers[option].add_argument(
                    "--nohup", action="store_true",
                    help="Ignore SIGHUP and redirect output to nohup.out")
        # Docs
        subparsers["docs"].add_argument(
            "-o", "--out_file", default=const.COMMANDS_DOC_PATH, help="Path to output file")
        # Patch
        self.config_files = [
            "config.yaml",
            "markov.yaml",
            "secret.yaml",
        ]
        subparsers["patch"].add_argument(
            "file", nargs='?', default="all",
            help='Config file to patch', choices=["all", *self.config_files])
        self.args = self._parser.parse_args()
        if self.args.action is None:
            self._parser.print_help()
        else:
            getattr(self, self.args.action)()

    def start(self):
        """Start the bot"""
        if self.args.autoupdate:
            return self.autoupdate()
        importlib.import_module("src.bot").start(self.args)

    def stop(self):
        """Stop the bot"""
        importlib.import_module("src.bot").stop(self.args)

    def restart(self):
        """Restart the bot"""
        bot = importlib.import_module("src.bot")
        bot.stop(self.args)
        bot.start(self.args)

    def suspend(self):
        """Stop the main bot and start mini-bot"""
        bot = importlib.import_module("src.bot")
        bot.stop(self.args)
        bot.start(self.args, main_bot=False)

    def test(self):
        """Launch tests"""
        importlib.import_module("src.test").start_testing()

    def docs(self):
        """Generate command docs"""
        importlib.import_module("tools.docs").main(self.args)

    def help(self):
        """Print help message"""
        self._parser.print_help()

    def patch(self):
        """Patch config"""
        importlib.import_module("tools.patch").main(self.args, self.config_files)

    def autoupdate(self):
        """Start autoupdate process for bot"""
        importlib.import_module("src.autoupdate").start(self.args)
