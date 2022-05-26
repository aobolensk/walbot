"""
WalBot launcher
"""

import argparse
import importlib
import inspect
import os
import signal
import sys
import threading
import time

import psutil

from src import const
from src.bot_cache import BotCache
from src.api.bot_instance import BotInstance
from src.ff import FF
from src.log import log


class Launcher:
    """This class parses provided command line options and dispatches execution depending on them."""

    def _get_argparser(self):
        parser = argparse.ArgumentParser(description='WalBot', formatter_class=argparse.RawTextHelpFormatter)
        subparsers = parser.add_subparsers(dest="action")
        subparsers = {
            cmd: subparsers.add_parser(
                cmd, help=getattr(self, cmd).__doc__, formatter_class=argparse.RawTextHelpFormatter)
            for cmd in list(filter(lambda _: not _.startswith('_') and not _.startswith('launch_'), dir(self)))
        }
        # Common
        for option in subparsers.keys():
            subparsers[option].add_argument(
                "--name", default="WalBot", help="Bot instance name")
        # Start
        subparsers["start"].add_argument(
            "--autoupdate", action="store_true",
            help="Start autoupdate process for bot")
        # Start & suspend
        for option in ("start", "restart", "suspend", "startmini", "stopmini"):
            subparsers[option].add_argument(
                "--fast_start", action="store_true",
                help=("Make bot start faster by disabling some optional checks:\n"
                      "- Disable Markov model check on start\n"
                      ))
            if sys.platform in ("linux", "darwin"):
                subparsers[option].add_argument(
                    "--nohup", action="store_true",
                    help="Ignore SIGHUP and redirect output to nohup.out")
        # MiniWalBot
        for option in ("suspend", "startmini"):
            subparsers[option].add_argument(
                "-m", "--message", default="<Maintenance break>",
                help="Message for MiniWalBot to type on every mention or command")
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
        # Test
        subparsers["test"].add_argument(
            "-v", "--verbose", action="store_true", help="Verbose", default=False)
        subparsers["test"].add_argument(
            "-vv", "--verbose2", action="store_true", help="Verbose (level2)", default=False)
        # Autocomplete
        subparsers["autocomplete"].add_argument("type", nargs=1, help="Shell type", choices=["bash"])
        return parser

    def _list_env_var_flags(self):
        log.debug2("--- Environment variable flags: ---")
        for key, value in FF.get_list().items():
            log.debug2(f"{key}: {value}")
        log.debug2("--- End of environment variable flags: ---")

    def __init__(self):
        self._parser = self._get_argparser()
        self.args = self._parser.parse_args()

    def _prepare_args(self):
        if self.args.action in ("start", "restart", "suspend", "startmini", "stopmini"):
            if sys.platform in ("linux", "darwin"):
                if self.args.nohup:
                    log.warning(
                        "You are using --nohup option. "
                        "Please note that currently SIGHUP signal is not ignored, "
                        "but output is redirected to nohup.out")

    def launch_bot(self):
        """Launch Discord bot instance"""
        self._list_env_var_flags()
        self._prepare_args()
        if self.args.action is None:
            self._parser.print_help()
        else:
            getattr(self, self.args.action)()

    def _stop_signal_handler(self, sig, frame):
        for backend in self.backends:
            backend.stop(self.args)
            log.debug2("Stopped backend: " + backend.__class__.__name__)
        log.info('Stopped the bot!')
        sys.exit(const.ExitStatus.NO_ERROR)

    def start(self, main_bot=True):
        """Start the bot"""
        if main_bot and self.args.autoupdate:
            return self.autoupdate()
        self.backends = []
        for backend in os.listdir(const.BOT_BACKENDS_PATH):
            if (os.path.isdir(os.path.join(const.BOT_BACKENDS_PATH, backend)) and
                    os.path.exists(os.path.join(const.BOT_BACKENDS_PATH, backend, "instance.py"))):
                module = importlib.import_module(f"src.backend.{backend}.instance")
                instances = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                             if issubclass(obj[1], BotInstance) and obj[1] != BotInstance]
                instance = instances[0]()
                self.backends.append(instance)
                log.debug2("Detected backend: " + instance.__class__.__name__)
        for backend in self.backends:
            thread = threading.Thread(target=backend.start, args=(self.args, main_bot))
            thread.setDaemon(True)
            thread.start()
            log.debug2("Started backend: " + backend.__class__.__name__)
        signal.signal(signal.SIGINT, self._stop_signal_handler)
        signal.pause()

    def _stop_bot_process(self, _, main_bot=True):
        if not BotCache(main_bot).exists():
            return log.error("Could not stop the bot (cache file does not exist)")
        bot_cache = BotCache(main_bot).parse()
        pid = bot_cache["pid"]
        if pid is None:
            return log.error("Could not stop the bot (cache file does not contain pid)")
        if psutil.pid_exists(pid):
            if sys.platform == "win32":
                # Reference to the original solution:
                # https://stackoverflow.com/a/64357453
                import ctypes

                kernel = ctypes.windll.kernel32
                kernel.FreeConsole()
                kernel.AttachConsole(pid)
                kernel.SetConsoleCtrlHandler(None, 1)
                kernel.GenerateConsoleCtrlEvent(0, 0)
            else:
                os.kill(pid, signal.SIGINT)
            while psutil.pid_exists(pid):
                log.debug("Bot is still running. Please, wait...")
                time.sleep(0.5)
            log.info("Bot is stopped!")
        else:
            log.error("Could not stop the bot (bot is not running)")
            BotCache(main_bot).remove()

    def stop(self):
        """Stop the bot"""
        self._stop_bot_process(self.args)

    def restart(self):
        """Restart the bot"""
        self._stop_bot_process(self.args)
        self.start()

    def suspend(self):
        """Stop the main bot and start mini-bot"""
        self._stop_bot_process(self.args)
        self.start(main_bot=False)

    def startmini(self):
        """Start mini-bot"""
        self.start(main_bot=False)

    def stopmini(self):
        """Stop mini-bot"""
        self._stop_bot_process(self.args, main_bot=False)

    def test(self):
        """Launch tests"""
        importlib.import_module("src.test").start_testing(self.args)

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

    def mexplorer(self):
        """Markov model explorer"""
        importlib.import_module("tools.mexplorer").main(self.args)

    def autocomplete(self):
        """Update shell autocompletion scripts (requires `shtab` dependency)"""
        importlib.import_module("src.utils").dump_autocomplete_script(next(iter(self.args.type), None), self._parser)
