import importlib
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from typing import Optional

import git
import psutil

from src import const
from src.bot_cache import BotCache
from src.ff import FF
from src.info import BotInfo
from src.log import log
from src.mail import Mail
from src.utils import Util


@dataclass
class AutoUpdateContext:
    config_version: Optional[str] = None
    markov_version: Optional[str] = None
    secret_version: Optional[str] = None
    repo: Optional[git.Repo] = None

    def __init__(self) -> None:
        self.config_version = const.CONFIG_VERSION
        self.markov_version = const.MARKOV_CONFIG_VERSION
        self.secret_version = const.SECRET_CONFIG_VERSION
        try:
            self.repo = git.Repo(search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            raise RuntimeError(
                "Failed to find walbot git repo. Autoupdate function is available only for git repository")

    def check_versions(self) -> bool:
        """Compare versions from updated version.py with current ones"""
        import src.version as ver
        importlib.reload(ver)
        updated = False
        if self.config_version != ver.CONFIG_VERSION:
            self.config_version = ver.CONFIG_VERSION
            updated = True
        if self.markov_version != ver.MARKOV_CONFIG_VERSION:
            self.markov_version = ver.MARKOV_CONFIG_VERSION
            updated = True
        if self.secret_version != ver.SECRET_CONFIG_VERSION:
            self.secret_version = ver.SECRET_CONFIG_VERSION
            updated = True
        log.debug(f"Config versions were{'' if updated else ' not'} updated")
        return updated


def get_autoupdate_error_message(error_string: str) -> str:
    """Forms error message for autoupdate"""
    return (
        error_string +
        "\n"
        f"Backtrace:\n"
        f"{''.join(traceback.format_stack())}\n"
        f"Details:\n" +
        BotInfo().get_full_info(2) + "\n"
    )


def check_updates(context: AutoUpdateContext) -> bool:
    """Function that performs updates check. It is called periodically"""
    secret_config = Util.read_config_file(const.SECRET_CONFIG_PATH)
    if secret_config is None:
        log.error("Failed to read secret config file")
        return False
    mail = Mail(secret_config)
    old_sha = context.repo.head.object.hexsha
    try:
        context.repo.remotes.origin.fetch()
    except Exception as e:
        mail.send(
            secret_config.admin_email_list,
            "Autoupdate error",
            get_autoupdate_error_message(f"Failed to fetch updates from remote: {e}"))
        log.error(f"Fetch failed: {e}. Skipping this cycle, will try to update on the next one")
        return False
    new_sha = context.repo.remotes.origin.refs['master'].object.name_rev.split()[0]
    log.debug(f"{old_sha} {new_sha}")
    if not FF.is_enabled("WALBOT_TEST_AUTO_UPDATE") and old_sha == new_sha:
        log.debug("No new updates")
        return False
    bot_cache = importlib.import_module("src.bot_cache").BotCache(True).parse()
    if bot_cache is None:
        log.warning("Could not read bot cache. Skipping this cycle, will try to update on the next one")
        return False
    if "do_not_update" not in bot_cache.keys():
        log.warning(
            "Could not find 'do_not_update' field in bot cache. "
            "Skipping this cycle, will try to update on the next one")
        return False
    if bot_cache["do_not_update"]:
        log.debug("Automatic update is not permitted. Skipping this cycle, will try to update on the next one")
        return False
    context.repo.git.reset("--hard")
    try:
        g = git.cmd.Git(const.WALBOT_DIR)
        g.pull()
    except git.exc.GitCommandError as e:
        if "Connection timed out" in e.stderr or "Could not resolve host" in e.stderr:
            mail.send(
                secret_config.admin_email_list,
                "Autoupdate error",
                get_autoupdate_error_message(f"{e.command}: {e.stderr}"))
            log.warning(f"{e.command}: {e.stderr}")
        else:
            raise e
    p = subprocess.run(f"{sys.executable} -m pip install -r requirements.txt", shell=True, capture_output=True)
    if p.returncode != 0:
        mail.send(
            secret_config.admin_email_list,
            "Autoupdate error",
            get_autoupdate_error_message(
                f"Failed to fetch requirements.txt. Return code: {p.returncode}\n"
                f"stdout:\n{p.stdout.decode('utf-8')}\n"
                f"stderr:\n{p.stderr.decode('utf-8')}\n"))
    minibot_response = "WalBot automatic update is in progress. Please, wait..."
    subprocess.call(f"{sys.executable} walbot.py startmini --message '{minibot_response}' --nohup &", shell=True)
    p = subprocess.run(f"{sys.executable} walbot.py stop", shell=True)
    if p.returncode != 0:
        mail.send(
            secret_config.admin_email_list,
            "Autoupdate error",
            get_autoupdate_error_message(f"Failed to stop the bot. Return code: {p.returncode}"))
    if context.check_versions():
        subprocess.call(f"{sys.executable} walbot.py patch", shell=True)
    subprocess.call(
        f"{sys.executable} walbot.py start --name '{const.INSTANCE_NAME}' "
        "--fast_start --nohup &", shell=True)
    while True:
        time.sleep(1)
        bot_cache = importlib.import_module("src.bot_cache").BotCache(True).parse()
        if bot_cache is not None and bot_cache["ready"]:
            log.debug("Stopping minibot...")
            p = subprocess.run(f"{sys.executable} walbot.py stopmini", shell=True)
            stopmini_attempt = 0
            stopmini_error = False
            while p.returncode != 0:
                time.sleep(10)
                p = subprocess.run(f"{sys.executable} walbot.py stopmini", shell=True)
                log.debug(f"Stopping minibot: {p} (attempt: {stopmini_attempt})")
                stopmini_attempt += 1
                if stopmini_attempt > 10:
                    mail.send(
                        secret_config.admin_email_list,
                        "Autoupdate error",
                        get_autoupdate_error_message(f"Failed to stop minibot. Return code: {p.returncode}"))
                    stopmini_error = True
                    break
            if not stopmini_error:
                log.info("Bot is fully loaded. MiniWalBot is stopped.")
            else:
                log.warning("Failed to stop minibot!")
            break
        log.debug("Bot is not fully loaded yet. Waiting...")
    return True


def at_start() -> None:
    """Autoupdate initialization"""
    if not os.path.isfile(const.BOT_CACHE_FILE_PATH):
        log.debug("Bot is not started! Starting...")
        subprocess.call(
            f"{sys.executable} walbot.py start --name '{const.INSTANCE_NAME}' "
            "--fast_start --nohup &", shell=True)
    else:
        bot_cache = BotCache(True).parse()
        pid = None
        if bot_cache is not None:
            pid = bot_cache["pid"]
        if pid is not None and psutil.pid_exists(pid):
            log.debug("Bot is already started in different shell. Starting autoupdate routine.")
        else:
            if os.path.isfile(const.BOT_CACHE_FILE_PATH):
                os.remove(const.BOT_CACHE_FILE_PATH)
            log.debug("Bot is not started! Starting...")
            subprocess.call(f"{sys.executable} walbot.py start --fast_start --nohup &", shell=True)


def at_failure(e: Exception) -> None:
    """Autoupdate fatal error handling"""
    log.error(f"Fatal error: {e}")
    secret_config = Util.read_config_file(const.SECRET_CONFIG_PATH)
    if secret_config is None:
        return log.error("Failed to read secret config file")
    mail = Mail(secret_config)
    mail.send(
        secret_config.admin_email_list,
        "Autoupdate error",
        get_autoupdate_error_message(
            f"Autoupdate fatal error: {e}"))


def at_exit(e: Exception) -> None:
    """Autoupdate finalize"""
    if os.path.isfile(const.BOT_CACHE_FILE_PATH):
        os.remove(const.BOT_CACHE_FILE_PATH)
    if os.path.isfile(const.MINIBOT_CACHE_FILE_PATH):
        os.remove(const.MINIBOT_CACHE_FILE_PATH)
