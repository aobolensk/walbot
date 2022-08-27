import functools

from telegram.ext import CommandHandler

from src.api.command import SupportedPlatforms
from src.backend.telegram.command import command_handler
from src.config import bc


class CommonCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        for cmd_name, command in bc.executor.commands.items():
            if command.supported_platforms & SupportedPlatforms.TELEGRAM:
                dispatcher.add_handler(
                    CommandHandler(cmd_name, functools.partial(command_handler, cmd_name), run_async=True))
