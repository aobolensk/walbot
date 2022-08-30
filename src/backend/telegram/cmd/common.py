import functools

from telegram.ext import CommandHandler, Dispatcher

from src.api.command import Command, SupportedPlatforms
from src.backend.telegram.command import command_handler
from src.config import bc


class CommonCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher: Dispatcher) -> None:
        for command in bc.executor.commands.values():
            self.add_handler(dispatcher, command)

    @staticmethod
    def add_handler(dispatcher: Dispatcher, command: Command) -> None:
        if command.supported_platforms & SupportedPlatforms.TELEGRAM:
            bc.telegram.handlers[command.command_name] = CommandHandler(
                command.command_name,
                functools.partial(command_handler, command.command_name), run_async=True)
            dispatcher.add_handler(bc.telegram.handlers[command.command_name])

    @staticmethod
    def remove_handler(dispatcher: Dispatcher, cmd_name: str) -> None:
        dispatcher.remove_handler(bc.telegram.handlers[cmd_name])
