#!/usr/bin/env python3
import argparse
import importlib
import sys

from src import const


class Launcher:
    def __init__(self):
        parser = argparse.ArgumentParser(description='WalBot', formatter_class=argparse.RawTextHelpFormatter)
        subparsers = parser.add_subparsers(dest="action")
        sp = dict([  # subparsers
            (cmd, subparsers.add_parser(cmd, help=getattr(self, cmd).__doc__))
            for cmd in list(filter(lambda _: not _.startswith('_'), dir(self)))
        ])
        # Start & suspend
        for x in ("start", "restart", "suspend"):
            sp[x].add_argument("--fast_start", action="store_true",
                               help="Disable some things to make bot start faster:\n" +
                                    "- Disable Markov model check on start\n")
            sp[x].add_argument("--patch", action="store_true",
                               help="Call script for patching config files before starting the bot")
            if sys.platform in ("linux", "darwin"):
                sp[x].add_argument("--nohup", action="store_true",
                                   help="Ignore SIGHUP and redirect output to nohup.out")
        # Docs
        sp["docs"].add_argument("-o", "--out_file", default=const.COMMANDS_DOC_PATH,
                                help="Path to output file")
        # Patch
        self.config_files = [
            "config.yaml",
            "markov.yaml",
            "secret.yaml",
        ]
        sp["patch"].add_argument("file", nargs='?', default="all", help='Config file to patch',
                                 choices=["all", *self.config_files])
        self.args = parser.parse_args()
        if self.args.action is None:
            parser.print_help()
        else:
            getattr(self, self.args.action)()

    def start(self):
        """Start the bot"""
        importlib.import_module("src.bot").start(self.args)

    def stop(self):
        """Stop the bot"""
        importlib.import_module("src.bot").stop()

    def restart(self):
        """Restart the bot"""
        bot = importlib.import_module("src.bot")
        bot.stop()
        bot.start(self.args)

    def suspend(self):
        """Stop the main bot and start mini-bot"""
        self.stop()
        importlib.import_module("src.bot").start(self.args, main_bot=False)

    def docs(self):
        """Generate command docs"""
        importlib.import_module("tools.docs").main(self.args)

    def patch(self):
        """Patch config"""
        importlib.import_module("tools.patch").main(self.args, self.config_files)


def main():
    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 5):
        print("Python {}.{}.{} is not supported. You need Python 3.5+".format(
              sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        sys.exit(1)
    Launcher()


if __name__ == "__main__":
    main()
