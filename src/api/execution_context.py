from abc import abstractmethod

from src import const


class ExecutionContext:
    def __init__(self) -> None:
        self.platform = "<unknown>"
        self.permission_level = const.Permission.USER
        self.silent = False

    @abstractmethod
    def send_message(self, message: str, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def disable_pings(self, message: str) -> None:
        pass

    @abstractmethod
    def message_author(self) -> None:
        pass
