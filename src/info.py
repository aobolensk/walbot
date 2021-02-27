import datetime

import git

from src.config import bc


class BotInfo:
    def _get_repo(self):
        try:
            return git.Repo(search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            return

    @property
    def version(self):
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        sha = repo.head.object.hexsha
        return sha

    @property
    def version_time(self):
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        time = repo.head.object.committed_datetime
        return time

    @property
    def uptime(self):
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
