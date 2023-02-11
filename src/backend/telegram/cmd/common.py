from telegram.ext import Application

from src.api.command import SupportedPlatforms
from src.backend.telegram.command import add_handler, remove_handler
from src.config import bc


class CommonCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, app: Application) -> None:
        for command in bc.executor.commands.values():
            if command.supported_platforms & SupportedPlatforms.TELEGRAM:
                add_handler(app, command)

    def remove_handler(app: Application, cmd_name: str) -> None:
        remove_handler(app, cmd_name)
