import json
import os
from typing import Dict, Optional

import psutil

from src import const
from src.log import log


class BotCache:
    def __init__(self, main_bot) -> None:
        self.path = const.BOT_CACHE_FILE_PATH if main_bot else const.MINIBOT_CACHE_FILE_PATH

    def parse(self) -> Optional[Dict]:
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

    def dump(self, cache_dict) -> None:
        with open(self.path, 'w') as f:
            json.dump(cache_dict, f)

    def remove(self) -> None:
        os.remove(self.path)

    def exists(self) -> bool:
        return os.path.exists(self.path)
