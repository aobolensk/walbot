from abc import ABC, abstractmethod
from typing import Any

from src import const


class ExecutionContext(ABC):
    def __init__(self) -> None:
        self.platform = "<unknown>"
        self.permission_level = const.Permission.USER
        self.silent = False
        self.user = None

    @abstractmethod
    async def send_message(self, message: str, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def reply(self, message: str, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def send_direct_message(self, user_id: int, message: str, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def disable_pings(self, message: str) -> str:
        pass

    @abstractmethod
    def message_author(self) -> str:
        pass

    @abstractmethod
    def message_author_id(self) -> int:
        pass

    @abstractmethod
    def channel_name(self) -> str:
        pass

    @abstractmethod
    def channel_id(self) -> int:
        pass

    @abstractmethod
    def bot_user_id(self) -> int:
        pass
