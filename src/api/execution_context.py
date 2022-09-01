from abc import abstractmethod
from typing import Any

from src import const


class ExecutionContext:
    def __init__(self) -> None:
        self.platform = "<unknown>"
        self.permission_level = const.Permission.USER
        self.silent = False

    @abstractmethod
    async def send_message(self, message: str, *args, **kwargs) -> Any:
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
