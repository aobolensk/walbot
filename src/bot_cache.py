import json
import os

import psutil

from src import const
from src.log import log


class BotCache:
    @staticmethod
    def file_path(main_bot):
        return const.BOT_CACHE_FILE_PATH if main_bot else const.MINIBOT_CACHE_FILE_PATH

    @staticmethod
    def parse(main_bot):
        if os.path.exists(BotCache.file_path(main_bot)):
            cache = None
            with open(BotCache.file_path(main_bot), 'r') as f:
                cache = json.load(f)
            if cache is not None:
                if "pid" not in cache or not psutil.pid_exists(int(cache["pid"])):
                    log.warning("Could validate pid from .bot_cache")
                    os.remove(BotCache.file_path(main_bot))
                    return
                return cache

    @staticmethod
    def dump(main_bot, cache_dict):
        with open(BotCache.file_path(main_bot), 'w') as f:
            print(json.dumps(cache_dict), file=f)

    @staticmethod
    def remove(main_bot):
        os.remove(BotCache.file_path(main_bot))

    @staticmethod
    def exists(main_bot):
        return os.path.exists(BotCache.file_path(main_bot))
