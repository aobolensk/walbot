from telegram import Update

from src.api.command import ExecutionContext
from src.backend.telegram.util import reply


class TelegramExecutionContext(ExecutionContext):
    def __init__(self, update: Update) -> None:
        super().__init__()
        self.platform = "telegram"
        self.update = update

    def send_message(self, message: str) -> None:
        reply(self.update, message)

    def disable_pings(self, message: str) -> None:
        # TODO: implement
        return message
