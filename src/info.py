import datetime
import importlib
from typing import Dict, Optional

import git

from src.config import bc


class BotInfo:
    """Get info about walbot instance"""

    def _get_repo(self) -> Optional[git.Repo]:
        try:
            return git.Repo(search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            return

    @property
    def version(self) -> str:
        """Get walbot repo commit SHA"""
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        sha = repo.head.object.hexsha
        return sha

    @property
    def commit_name(self) -> str:
        """Get walbot repo commit name"""
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        commit = repo.head.commit.message.splitlines()[0].strip()
        return commit

    @property
    def branch_name(self) -> str:
        """Get walbot repo branch name"""
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        branch = repo.active_branch.name
        return branch

    @property
    def is_version_dirty(self) -> bool:
        """Get walbot repo dirtyness"""
        repo = self._get_repo()
        if repo is None:
            return False
        return repo.is_dirty()

    @property
    def version_time(self) -> str:
        """Get walbot repo last commit date/time"""
        repo = self._get_repo()
        if repo is None:
            return "<unknown>"
        time = repo.head.object.committed_datetime
        return time

    def query_dependencies_info(self) -> Dict[str, str]:
        """Get dict with walbot dependencies versions"""
        res = {}
        res["discord.py"] = importlib.import_module("discord").__version__
        res["numpy"] = importlib.import_module("numpy").__version__
        res["requests"] = importlib.import_module("requests").__version__
        res["numba"] = importlib.import_module("numba").__version__
        res["psutil"] = importlib.import_module("psutil").__version__
        res["dateutil"] = importlib.import_module("dateutil").__version__
        res["GitPython"] = importlib.import_module("git").__version__
        res["PyYAML"] = importlib.import_module("yaml").__version__
        res["youtube_dl"] = importlib.import_module("youtube_dl.update").__version__
        return res

    @property
    def uptime(self) -> str:
        """Get walbot uptime"""
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
