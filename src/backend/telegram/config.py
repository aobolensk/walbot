import uuid
from typing import Any, Dict, Set


class TelegramConfig:
    def __init__(self) -> None:
        self.channel_whitelist: Set[str] = set()
        self.passphrase = uuid.uuid4().hex
        self.users: Dict[str, Any] = dict()
