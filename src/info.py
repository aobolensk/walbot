import datetime
import os

from src.config import bc


class BotInfo:
    @property
    def version(self):
        if not os.path.exists(os.path.join(os.getcwd(), ".git")):
            return "Unable to get version (.git folder is not found)"
        if not os.path.exists(os.path.join(os.getcwd(), ".git/HEAD")):
            return "Unable to get version (.git/HEAD file is not found)"
        with open(os.path.join(os.getcwd(), ".git/HEAD")) as f:
            branch = f.readline()
            if branch[:5] != "ref: ":
                return "Unable to get version (.git/HEAD format is unknown)"
            branch = branch[5:].strip()
        if not os.path.exists(os.path.join(os.getcwd(), ".git/" + branch)):
            return "Unable to get version (.git/" + branch + " file is not found)"
        with open(os.path.join(os.getcwd(), ".git/" + branch)) as f:
            commit_hash = f.readline()
        return commit_hash[:-1]

    @property
    def uptime(self):
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}:{hours:02}:{minutes:02}:{seconds:02}"
