import importlib
import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

import git

from src import const
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
        g = git.cmd.Git(os.getcwd())
        g.pull()
    except git.exc.GitCommandError as e:
        if "Connection timed out" in e.stderr or "Could not resolve host" in e.stderr:
            log.warning(f"{e.command}: {e.stderr}")
        else:
            raise e
    new_sha = context.repo.head.object.hexsha
    log.debug(f"{old_sha} {new_sha}")
    if old_sha == new_sha:
        return log.debug("No new updates")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    minibot_response = "WalBot automatic update is in progress. Please, wait..."
    os.system(f"{sys.executable} walbot.py startmini --message '{minibot_response}' --nohup &")
    os.system(f"{sys.executable} walbot.py stop")
    if context.check_versions():
        os.system(f"{sys.executable} walbot.py patch")
    os.system(f"{sys.executable} walbot.py start --nohup &")
    while True:
        time.sleep(1)
        bot_cache = importlib.import_module("src.bot_cache").BotCache.parse(True)
        if bot_cache is not None and bot_cache["ready"]:
            os.system(f"{sys.executable} walbot.py stopmini")
            log.info("Bot is fully loaded. MiniWalBot is stopped.")
            break
        log.debug("Bot is not fully loaded yet. Waiting...")


def at_start() -> None:
    if not os.path.isfile(const.BOT_CACHE_FILE_PATH):
        log.debug("Bot is not started! Starting...")
        os.system(f"{sys.executable} walbot.py start --nohup &")
    else:
        log.debug("Bot is already started in different shell. Starting autoupdate routine.")


def at_failure(e: Exception) -> None:
    os.system(f"{sys.executable} walbot.py stop")


def at_exit() -> None:
    os.remove(const.BOT_CACHE_FILE_PATH)
