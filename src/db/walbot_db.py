import hashlib
import os
from typing import Optional

import pymongo  # type:ignore
from pymongo.collection import Collection  # type:ignore
from pymongo.errors import ServerSelectionTimeoutError  # type:ignore

from src.log import log


class WalbotDatabase:
    url: str = "mongodb://localhost:27017/"

    def __init__(self) -> None:
        self._db_name = self.get_db_name()
        self.markov: Optional[Collection] = None
        self.connect()

    def connect(self) -> None:
        self._db_client = pymongo.MongoClient(self.url, serverSelectionTimeoutMS=10, connectTimeoutMS=20000)
        try:
            info = self._db_client.server_info()
            log.debug(f"Mongo connection initialized: {info['version']}")
        except ServerSelectionTimeoutError as e:
            log.error(f"Mongo connection failed: {e}")
        self._db = self._db_client[self._db_name]
        self.markov = self._db["markov"]

    def disconnect(self) -> None:
        self._db_client.close()

    @staticmethod
    def get_db_name() -> str:
        return f"walbot-{os.getcwd().split('/')[-1]}-{hashlib.sha256(os.getcwd().encode('utf-8')).hexdigest()[:8]}"
