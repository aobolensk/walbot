import importlib
import os
import platform
import sys
from typing import Dict, Optional

import git

from src import const
from src.config import bc
from src.shell import Shell
from src.utils import Time, Util


class BotInfo:
    """Get info about walbot instance"""

    def _get_repo(self) -> Optional[git.Repo]:
        try:
            return git.Repo(search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            return None

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
        return str(commit)

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

    def _get_version_from_requirements_txt(self, dependency_name: str) -> str:
        """Get version of dependency from requirements.txt"""
        with open("requirements.txt") as f:
            for line in f:
                if line.startswith(dependency_name):
                    return line.split("==")[1].strip()
        return "<unknown>"

    def query_dependencies_info(self) -> Dict[str, str]:
        """Get dict with walbot dependencies versions"""
        res = {}
        res["py-cord (former discord.py)"] = importlib.import_module("discord").__version__
        res["numpy"] = importlib.import_module("numpy").__version__
        res["requests"] = importlib.import_module("requests").__version__
        try:
            res["numba"] = importlib.import_module("numba").__version__
        except ImportError:
            res["numba"] = "N/A"
        res["psutil"] = importlib.import_module("psutil").__version__
        res["dateutil"] = importlib.import_module("dateutil").__version__
        res["GitPython"] = importlib.import_module("git").__version__
        res["PyYAML"] = importlib.import_module("yaml").__version__
        res["yt_dlp"] = importlib.import_module("yt_dlp.update").__version__
        res["python-telegram-bot"] = importlib.import_module("telegram").__version__
        res["aiogoogletrans"] = importlib.import_module("aiogoogletrans").__version__
        res["nest-asyncio"] = self._get_version_from_requirements_txt("nest-asyncio")
        res["python-magic"] = self._get_version_from_requirements_txt("python-magic")
        return res

    @property
    def uptime(self) -> str:
        """Get walbot uptime"""
        days, remainder = divmod(
            int((Time().now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"

    def get_full_info(self, verbosity) -> str:
        result = f"{const.INSTANCE_NAME} (WalBot instance)\n"
        result += "Backends:\n"
        if bc.be.is_running(const.BotBackend.DISCORD):
            result += f"    Discord: on ({bc.discord.bot_user})\n"
        else:
            result += "    Discord: off\n"
        if bc.be.is_running(const.BotBackend.TELEGRAM):
            result += f"    Telegram: on ({bc.telegram.bot_username})\n"
        else:
            result += "    Telegram: off\n"
        if bc.be.is_running(const.BotBackend.REPL):
            result += "    REPL: on\n"
        else:
            result += "    REPL: off\n"
        result += (
            f"Source code: {const.GIT_REPO_LINK}\n"
            f"Version: {self.version}{'-dirty' if self.is_version_dirty else ''} (updated at {self.version_time})\n"
            f"Uptime: {self.uptime}\n"
        )
        if verbosity >= const.Verbosity.VERBOSE:
            result += (
                f"Deployment time: {bc.deployment_time}\n"
                f"Commit name: `{self.commit_name}`\n"
                f"Branch name: {self.branch_name}\n"
                f"Python interpreter: {platform.python_implementation()} {platform.python_version()} "
                f"({', '.join(platform.python_build())}) [{platform.python_compiler()}]\n"
            )
            # Dependencies info
            result += "Dependencies:\n"
            result += '\n'.join(f"    {name}: {ver}" for name, ver in self.query_dependencies_info().items()) + '\n'
        if verbosity >= const.Verbosity.VERBOSE2:
            result += f"OS info: {' '.join(platform.uname())}\n"
            result += f"Working directory: {const.WALBOT_DIR}\n"
            if sys.platform == "linux":
                if os.path.isfile("/etc/lsb-release"):
                    with open("/etc/lsb-release") as f:
                        result += f"Linux distro information:\n{f.read().strip()}\n"
                elif os.path.isfile("/etc/os-release"):
                    with open("/etc/os-release") as f:
                        result += f"Linux distro information:\n{f.read().strip()}\n"
            elif sys.platform == "darwin":
                result += "macOS version: " + Shell.run('sw_vers -productName').stdout.strip() + " "
                result += Shell.run('sw_vers -productVersion').stdout.strip() + " "
                result += "(" + Shell.run('sw_vers -buildVersion').stdout.strip() + ")\n"
            elif sys.platform == "win32":
                result += "Windows version: " + platform.platform()
            result += "Proxy:\n"
            result += f"    HTTP proxy: {Util.proxy.http() or '<no proxy>'}\n"
            result += f"    HTTPS proxy: {Util.proxy.https() or '<no proxy>'}\n"
        return result
