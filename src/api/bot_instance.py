from abc import abstractmethod


class BotInstance:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def start(self, args) -> None:
        pass

    @abstractmethod
    def stop(self, args) -> None:
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__
