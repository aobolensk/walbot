import datetime

import git

from src.config import bc


class BotInfo:
    @property
    def version(self):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return sha

    @property
    def version_time(self):
        repo = git.Repo(search_parent_directories=True)
        time = repo.head.object.committed_datetime
        return time

    @property
    def uptime(self):
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
