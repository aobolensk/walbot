import json
import os

import psutil

from src import const
from src.log import log


class BotCache:
    def __init__(self, main_bot) -> None:
        self.path = const.BOT_CACHE_FILE_PATH if main_bot else const.MINIBOT_CACHE_FILE_PATH

    def parse(self):
        if os.path.exists(self.path):
            cache = None
            with open(self.path, 'r') as f:
                cache = json.load(f)
            if cache is not None:
                if "pid" not in cache or not psutil.pid_exists(int(cache["pid"])):
                    log.warning("Could validate pid from .bot_cache")
                    os.remove(self.path)
                    return
                return cache

    def dump(self, cache_dict):
        with open(self.path, 'w') as f:
            print(json.dumps(cache_dict), file=f)

    def remove(self):
        os.remove(self.path)

    def exists(self):
        return os.path.exists(self.path)
