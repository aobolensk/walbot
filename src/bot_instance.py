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
