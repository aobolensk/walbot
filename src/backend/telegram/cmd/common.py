from telegram.ext import Dispatcher

from src.api.command import SupportedPlatforms
from src.backend.telegram.command import add_handler, remove_handler
from src.config import bc


class CommonCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher: Dispatcher) -> None:
        for command in bc.executor.commands.values():
            if command.supported_platforms & SupportedPlatforms.TELEGRAM:
                add_handler(dispatcher, command)

    def remove_handler(dispatcher: Dispatcher, cmd_name: str) -> None:
        remove_handler(dispatcher, cmd_name)
