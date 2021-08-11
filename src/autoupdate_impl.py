import importlib
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Optional

import git
import psutil

from src import const
from src.bot_cache import BotCache
from src.log import log


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
            log.error(
                "Failed to find walbot git repo. Autoupdate function is available only for git repository")

    def check_versions(self) -> bool:
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


def check_updates(context: AutoUpdateContext) -> bool:
    old_sha = context.repo.head.object.hexsha
    try:
        context.repo.remotes.origin.fetch()
    except Exception as e:
        return log.error(f"Fetch failed: {e}. Skipping this cycle, will try to update on the next one")
    new_sha = context.repo.remotes.origin.refs['master'].object.name_rev.split()[0]
    log.debug(f"{old_sha} {new_sha}")
    if old_sha == new_sha:
        return log.debug("No new updates")
    bot_cache = importlib.import_module("src.bot_cache").BotCache(True).parse()
    if bot_cache is None:
        return log.warning("Could not read bot cache. Skipping this cycle, will try to update on the next one")
    if "do_not_update" not in bot_cache.keys():
        return log.warning(
            "Could not find 'do_not_update' field in bot cache. "
            "Skipping this cycle, will try to update on the next one")
    if bot_cache["do_not_update"]:
        return log.debug("Automatic update is not permitted. Skipping this cycle, will try to update on the next one")
    context.repo.git.reset("--hard")
    try:
        g = git.cmd.Git(os.getcwd())
        g.pull()
    except git.exc.GitCommandError as e:
        if "Connection timed out" in e.stderr or "Could not resolve host" in e.stderr:
            log.warning(f"{e.command}: {e.stderr}")
        else:
            raise e
    subprocess.call(f"{sys.executable} -m pip install -r requirements.txt", shell=True)
    minibot_response = "WalBot automatic update is in progress. Please, wait..."
    subprocess.call(f"{sys.executable} walbot.py startmini --message '{minibot_response}' --nohup &", shell=True)
    subprocess.call(f"{sys.executable} walbot.py stop", shell=True)
    if context.check_versions():
        subprocess.call(f"{sys.executable} walbot.py patch", shell=True)
    subprocess.call(f"{sys.executable} walbot.py start --fast_start --nohup &", shell=True)
    while True:
        time.sleep(1)
        bot_cache = importlib.import_module("src.bot_cache").BotCache(True).parse()
        if bot_cache is not None and bot_cache["ready"]:
            subprocess.call(f"{sys.executable} walbot.py stopmini", shell=True)
            log.info("Bot is fully loaded. MiniWalBot is stopped.")
            break
        log.debug("Bot is not fully loaded yet. Waiting...")
    return True


def at_start() -> None:
    if not os.path.isfile(const.BOT_CACHE_FILE_PATH):
        log.debug("Bot is not started! Starting...")
        subprocess.call(f"{sys.executable} walbot.py start --fast_start --nohup &", shell=True)
    else:
        bot_cache = BotCache(True).parse()
        pid = bot_cache["pid"]
        if pid is not None and psutil.pid_exists(pid):
            log.debug("Bot is already started in different shell. Starting autoupdate routine.")
        else:
            os.remove(const.BOT_CACHE_FILE_PATH)
            log.debug("Bot is not started! Starting...")
            subprocess.call(f"{sys.executable} walbot.py start --fast_start --nohup &", shell=True)


def at_failure(e: Exception) -> None:
    pass


def at_exit() -> None:
    if os.path.isfile(const.BOT_CACHE_FILE_PATH):
        os.remove(const.BOT_CACHE_FILE_PATH)
