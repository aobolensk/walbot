import os
import time
import sys

import git

from src import const
from src.log import log


def check_updates(repo):
    old_sha = repo.head.object.hexsha
    g = git.cmd.Git(os.getcwd())
    g.pull()
    new_sha = repo.head.object.hexsha
    log.debug(f"{old_sha} {new_sha}")
    if (old_sha == new_sha):
        log.debug("No new updates")
        return
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    os.system(f"{sys.executable} walbot.py stop")
    os.system(f"{sys.executable} walbot.py start --nohup &")


def start(args):
    try:
        repo = git.Repo(search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        log.error("Failed to find walbot git repo. Autoupdate function is available only for git repository")
        return
    if not os.path.isfile(const.BOT_CACHE_FILE_PATH):
        log.debug("Bot is not started! Starting...")
        os.system(f"{sys.executable} walbot.py start --nohup &")
    try:
        while True:
            check_updates(repo)
            time.sleep(const.AUTOUPDATE_CHECK_INTERVAL)
    except KeyboardInterrupt:
        os.system(f"{sys.executable} walbot.py stop")
