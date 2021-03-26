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
    def commit_name(self):
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        commit = repo.head.commit.message.splitlines()[0].strip()
        return commit

    @property
    def branch_name(self):
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        branch = repo.active_branch.name
        return branch

    @property
    def is_version_dirty(self) -> bool:
        repo = self._get_repo()
        if repo is None:
            return False
        return repo.is_dirty()

    @property
    def version_time(self):
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        time = repo.head.object.committed_datetime
        return time

    def query_dependencies_info(self):
        res = {}
        import numpy
        res["numpy"] = numpy.__version__
        import discord
        ver = discord.version_info
        res["discord.py"] = f"{ver.major}.{ver.minor}.{ver.micro} {ver.releaselevel}"
        import requests
        res["requests"] = requests.__version__
        import numba
        res["numba"] = numba.__version__
        import psutil
        res["psutil"] = psutil.__version__
        import dateutil
        res["dateutil"] = dateutil.__version__
        import git
        res["GitPython"] = git.__version__
        import yaml
        res["PyYAML"] = yaml.__version__
        return res

    @property
    def uptime(self):
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
