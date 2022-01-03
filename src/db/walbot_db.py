import hashlib
import os
from typing import Optional

import pymongo
from pymongo.collection import Collection
from pymongo.errors import ServerSelectionTimeoutError

from src.log import log


class WalbotDatabase:
    url: str = "mongodb://localhost:27017/"
    _initialized: bool = False

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._db_name = self.get_db_name()
            self.markov: Optional[Collection] = None
            self.connect()
            self._initialized = True

    def connect(self) -> None:
        self._db_client = pymongo.MongoClient(self.url, serverSelectionTimeoutMS=10, connectTimeoutMS=20000)
        try:
            info = self._db_client.server_info()
            log.debug(f"Mongo connection initialized: {self.url} ({info['version']})")
        except ServerSelectionTimeoutError as e:
            log.error(f"Mongo connection failed: {e}")
        self._db = self._db_client[self._db_name]
        self.markov = self._db["markov"]
        self.bot_cache = self._db["bot_cache"]
        self.create_tables()

    def create_tables(self) -> None:
        if self.bot_cache.find_one({"type": "main_bot"}) is None:
            self.bot_cache.insert_one({
                "type": "main_bot",
                "pid": None,
                "ready": False,
                "do_not_update": False,
            })
            log.debug("Created main_bot bot_cache")
            assert self.bot_cache.find_one({"type": "main_bot"}) is not None
        if self.bot_cache.find_one({"type": "mini_bot"}) is None:
            log.debug2("Created new bot_cache collection")
            self.bot_cache.insert_one({
                "type": "mini_bot",
                "pid": None,
                "ready": False,
                "do_not_update": False,
            })
            log.debug("Created mini_bot bot_cache")
            assert self.bot_cache.find_one({"type": "mini_bot"}) is not None

    def disconnect(self) -> None:
        self._db_client.close()

    @staticmethod
    def get_db_name() -> str:
        return f"walbot-{os.getcwd().split('/')[-1]}-{hashlib.sha256(os.getcwd().encode('utf-8')).hexdigest()[:8]}"
