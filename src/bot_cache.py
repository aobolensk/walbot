import json
import os
import time
from typing import Dict, Optional

import psutil

from src import const
from src.log import log


class BotCache:
    _state = {
        "pid": os.getpid(),
        "ready": False,
        "do_not_update": False,
    }

    def get_state(self) -> dict:
        return self._state

    def __init__(self, main_bot) -> None:
        self.path = const.BOT_CACHE_FILE_PATH if main_bot else const.MINIBOT_CACHE_FILE_PATH

    def update(self, upd_dict):
        for key, value in upd_dict.items():
            self._state[key] = value

    def parse(self) -> Optional[Dict]:
        if os.path.exists(self.path):
            cache = None
            for _ in range(10):
                try:
                    with open(self.path, 'r') as f:
                        cache = json.load(f)
                    if cache is not None:
                        if "pid" not in cache or not psutil.pid_exists(int(cache["pid"])):
                            log.warning("Could validate pid from .bot_cache")
                            os.remove(self.path)
                            return
                        return cache
                except json.decoder.JSONDecodeError:
                    time.sleep(0.5)

    def dump_to_file(self) -> None:
        with open(self.path, 'w') as f:
            json.dump(self._state, f)

    def remove(self) -> bool:
        try:
            os.remove(self.path)
            return True
        except FileNotFoundError:
            return False

    def exists(self) -> bool:
        return os.path.exists(self.path)
