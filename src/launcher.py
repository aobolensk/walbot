"""
WalBot launcher
"""

import argparse
import asyncio
import importlib
import inspect
import os
import shutil
import signal
import sys
import threading
import time
import zipfile
from types import FrameType

import nest_asyncio
import psutil

from src import const
from src.algorithms import precompile_algs
from src.api.bot_instance import BotInstance
from src.api.command import SupportedPlatforms
from src.bot_cache import BotCache
from src.config import Config, SecretConfig, bc
from src.ff import FF
from src.info import BotInfo
from src.log import log
from src.markov import Markov, MarkovV2
from src.utils import Util


class Launcher:
    """This class parses provided command line options and dispatches execution depending on them."""

    def _get_argparser(self) -> argparse.ArgumentParser:
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
        # Start & restart
        for option in ("start", "restart"):
            subparsers[option].add_argument(
                "--autoupdate", action="store_true", help="Start autoupdate process for bot")
            subparsers[option].add_argument(
                "--ignore-version-check", action="store_true", help="Ignore version check")
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

    def _list_env_var_flags(self) -> None:
        log.debug2("--- Environment variable flags: ---")
        for key, value in FF.get_list().items():
            log.debug2(f"{key}: {value}")
        log.debug2("--- End of environment variable flags: ---")
        invalid_flags = FF.get_invalid_flags()
        if invalid_flags:
            log.warning(f"Invalid feature flags: {invalid_flags}")

    def __init__(self) -> None:
        self._parser = self._get_argparser()
        self.args = self._parser.parse_args()
        self._loop = asyncio.new_event_loop()

    def _prepare_args(self) -> None:
        if self.args.action in ("start", "restart", "suspend", "startmini", "stopmini"):
            if sys.platform in ("linux", "darwin"):
                if self.args.nohup:
                    fd = os.open(const.NOHUP_FILE_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
                    log.info(f"Output is redirected to {const.NOHUP_FILE_PATH}")
                    os.dup2(fd, sys.stdout.fileno())
                    os.dup2(sys.stdout.fileno(), sys.stderr.fileno())
                    os.close(fd)
                    log.warning(
                        "You are using --nohup option. "
                        "Please note that currently SIGHUP signal is not ignored, "
                        "but output is redirected to nohup.out")

    def launch_bot(self) -> const.ExitStatus:
        """Launch Discord bot instance"""
        self._list_env_var_flags()
        self._prepare_args()
        if self.args.action is None:
            self._parser.print_help()
            return const.ExitStatus.NO_ERROR
        else:
            return getattr(self, self.args.action)()

    def _stop_signal_handler(self, sig: int, frame: FrameType) -> None:
        for backend in self.backends:
            backend.stop(self.args)
            log.debug2("Stopped backend: " + backend.name)
        BotCache(True).remove()
        self._loop.run_until_complete(bc.plugin_manager.unload_plugins())
        bc.executor.store_persistent_state(bc.config.executor)
        bc.config.save(const.CONFIG_PATH, const.MARKOV_PATH, const.SECRET_CONFIG_PATH, wait=True)
        log.info('Stopped the bot!')
        sys.exit(const.ExitStatus.NO_ERROR)

    def _stop_signal_handler_mini(self, sig, frame):
        for backend in self.backends:
            backend.stop(self.args, main_bot=False)
            log.debug2("Stopped backend: " + backend.name)
        BotCache(False).remove()
        log.info('Stopped the minibot!')
        sys.exit(const.ExitStatus.NO_ERROR)

    def _read_configs(self, main_bot: bool = True) -> None:
        # Selecting YAML parser
        bc.yaml_loader, bc.yaml_dumper = Util.get_yaml()
        # Read configuration files
        bc.config = Util.read_config_file(const.CONFIG_PATH) or Config()
        bc.secret_config = Util.read_config_file(const.SECRET_CONFIG_PATH) or SecretConfig()
        bc.info = BotInfo()
        if not os.path.exists(const.IMAGES_DIRECTORY):
            os.makedirs(const.IMAGES_DIRECTORY)
        if not os.path.exists(const.BACKUP_DIRECTORY):
            os.makedirs(const.BACKUP_DIRECTORY)
        if main_bot:
            if not FF.is_enabled("WALBOT_FEATURE_MARKOV_MONGO"):
                bc.markov = Util.read_config_file(const.MARKOV_PATH)
                if bc.markov is None:
                    # Check available backups
                    markov_backups = sorted(
                        [x for x in os.listdir("backup") if x.startswith("markov_") and x.endswith(".zip")])
                    if markov_backups:
                        # Restore Markov model from backup
                        with zipfile.ZipFile("backup/" + markov_backups[-1], 'r') as zip_ref:
                            zip_ref.extractall(".")
                        log.info(f"Restoring Markov model from backup/{markov_backups[-1]}")
                        shutil.move(markov_backups[-1][:-4], "markov.yaml")
                        bc.markov = Util.read_config_file(const.MARKOV_PATH)
                        if bc.markov is None:
                            bc.markov = Markov()
                            log.warning("Failed to restore Markov model from backup. Creating new Markov model...")
                if bc.markov is None:
                    bc.markov = Markov()
                    log.info("Created empty Markov model")
            else:
                from src.db.walbot_db import WalbotDatabase
                db = WalbotDatabase()
                bc.markov = MarkovV2(db.markov)
        # Check config versions
        if main_bot:
            ok = True
            ok &= Util.check_version(
                "Config", bc.config.version, const.CONFIG_VERSION,
                solutions=[
                    "run patch tool",
                    "remove config.yaml (settings will be lost!)",
                ])
            ok &= Util.check_version(
                "Markov config", bc.markov.version, const.MARKOV_CONFIG_VERSION,
                solutions=[
                    "run patch tool",
                    "remove markov.yaml (Markov model will be lost!)",
                ])
            ok &= Util.check_version(
                "Secret config", bc.secret_config.version, const.SECRET_CONFIG_VERSION,
                solutions=[
                    "run patch tool",
                    "remove secret.yaml (your authentication tokens will be lost!)",
                ])
            if not ok and not self.args.ignore_version_check:
                sys.exit(const.ExitStatus.CONFIG_FILE_ERROR)

    def _append_backend(self, backend: str) -> None:
        module = importlib.import_module(f"src.backend.{backend}.instance")
        instances = [obj[1] for obj in inspect.getmembers(module, inspect.isclass)
                     if issubclass(obj[1], BotInstance) and obj[1] != BotInstance]
        instance = instances[0]()
        if not instance.has_credentials():
            return
        self.backends.append(instance)
        log.debug2("Detected backend: " + self.backends[-1].name)

    def start(self, main_bot: bool = True) -> const.ExitStatus:
        """Start the bot"""
        if main_bot and self.args.autoupdate:
            return self.autoupdate()
        self.backends = []
        self._read_configs(main_bot)
        bc.executor.load_commands()
        if not self.args.fast_start:
            bc.executor.export_help(SupportedPlatforms.TELEGRAM)
        bc.executor.load_persistent_state(bc.config.executor)
        bc.config.commands.update()
        nest_asyncio.apply()
        precompile_algs()

        # Saving bot_cache to safely stop it later
        bot_cache = BotCache(main_bot).parse()
        if bot_cache is not None:
            pid = bot_cache["pid"]
            if pid is not None and psutil.pid_exists(pid):
                log.error("Bot is already running!")
                return const.ExitStatus.GENERAL_ERROR
        BotCache(main_bot).dump_to_file()

        for backend in os.listdir(const.BOT_BACKENDS_PATH):
            if (os.path.isdir(os.path.join(const.BOT_BACKENDS_PATH, backend)) and
                    os.path.exists(os.path.join(const.BOT_BACKENDS_PATH, backend, "instance.py"))):
                if main_bot:
                    self._append_backend(backend)
                else:
                    if backend == "discord":
                        self._append_backend(backend)
        for backend in self.backends:
            thread = threading.Thread(target=backend.start, args=(self.args, main_bot))
            thread.setDaemon(True)
            thread.start()
            log.debug2("Started backend: " + backend.name)
        signal.signal(signal.SIGINT, self._stop_signal_handler if main_bot else self._stop_signal_handler_mini)
        if not self.backends:
            log.info(
                "No active backends found! "
                "Please setup config.yaml and secret.yaml to configure desired backends.")
            return const.ExitStatus.GENERAL_ERROR
        bc.plugin_manager.register()
        self._loop.create_task(bc.plugin_manager.load_plugins())
        self._loop.run_forever()
        if not sys.platform == "win32":
            signal.pause()
        else:
            while True:
                time.sleep(15)
        return const.ExitStatus.NO_ERROR

    def _stop_bot_process(self, _, main_bot: bool = True) -> const.ExitStatus:
        if not BotCache(main_bot).exists():
            log.error("Could not stop the bot (cache file does not exist)")
            return const.ExitStatus.GENERAL_ERROR
        bot_cache = BotCache(main_bot).parse()
        pid = bot_cache["pid"]
        if pid is None:
            log.error("Could not stop the bot (cache file does not contain pid)")
            return const.ExitStatus.GENERAL_ERROR
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
        return const.ExitStatus.NO_ERROR

    def stop(self) -> const.ExitStatus:
        """Stop the bot"""
        return self._stop_bot_process(self.args)

    def restart(self) -> const.ExitStatus:
        """Restart the bot"""
        ret = self._stop_bot_process(self.args)
        if ret != const.ExitStatus.NO_ERROR:
            return ret
        return self.start()

    def suspend(self) -> const.ExitStatus:
        """Stop the main bot and start mini-bot"""
        ret = self._stop_bot_process(self.args)
        if ret != const.ExitStatus.NO_ERROR:
            return ret
        return self.start(main_bot=False)

    def startmini(self) -> const.ExitStatus:
        """Start mini-bot"""
        return self.start(main_bot=False)

    def stopmini(self) -> const.ExitStatus:
        """Stop mini-bot"""
        return self._stop_bot_process(self.args, main_bot=False)

    def test(self) -> const.ExitStatus:
        """Launch tests"""
        return importlib.import_module("src.test").start_testing(self.args)

    def docs(self) -> const.ExitStatus:
        """Generate command docs"""
        return importlib.import_module("tools.docs").main(self.args)

    def help(self) -> const.ExitStatus:
        """Print help message"""
        self._parser.print_help()
        return const.ExitStatus.NO_ERROR

    def patch(self) -> const.ExitStatus:
        """Patch config"""
        return importlib.import_module("tools.patch").main(self.args, self.config_files)

    def autoupdate(self) -> const.ExitStatus:
        """Start autoupdate process for bot"""
        return importlib.import_module("src.autoupdate").start(self.args)

    def mexplorer(self) -> const.ExitStatus:
        """Markov model explorer"""
        return importlib.import_module("tools.mexplorer").main(self.args)

    def autocomplete(self) -> const.ExitStatus:
        """Update shell autocompletion scripts (requires `shtab` dependency)"""
        shell = next(iter(self.args.type), None)
        if shell == "bash":
            try:
                shtab = importlib.import_module("shtab")
            except ImportError:
                log.error("Shell autocompletion scripts update failed.")
                log.error(f"    Install `shtab`: {sys.executable} -m pip install shtab")
                return const.ExitStatus.GENERAL_ERROR
            result = shtab.complete(self._parser, shell="bash").replace("walbot.py", "./walbot.py")
            script_path = os.path.join(const.WALBOT_DIR, "tools", "autocomplete", "walbot-completion.bash")
            with open(script_path, "w") as f:
                print(result, file=f)
            log.info("bash autocompletion script has been updated: " + script_path)
            return const.ExitStatus.NO_ERROR
        else:
            log.error("Unsupported shell type")
            return const.ExitStatus.GENERAL_ERROR

    def setuphooks(self) -> const.ExitStatus:
        if sys.platform != "win32":
            shutil.copy(
                os.path.join("tools", "githooks", "pre-commit.linux"),
                os.path.join(".git", "hooks", "pre-commit"))
        else:
            shutil.copy(
                os.path.join("tools", "githooks", "pre-commit.windows"),
                os.path.join(".git", "hooks", "pre-commit"))
        log.info("Git hooks are successfully set up!")
        return const.ExitStatus.NO_ERROR

    def removehooks(self) -> const.ExitStatus:
        if os.path.exists(os.path.join(".git", "hooks", "pre-commit")):
            os.unlink(os.path.join(".git", "hooks", "pre-commit"))
        log.info("Git hooks are successfully removed!")
        return const.ExitStatus.NO_ERROR
