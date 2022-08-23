from telegram import Update

from src.api.execution_context import ExecutionContext
from src.backend.telegram.util import reply


class TelegramExecutionContext(ExecutionContext):
    def __init__(self, update: Update) -> None:
        super().__init__()
        self.platform = "telegram"
        self.update = update

    def send_message(self, message: str, *args, **kwargs) -> None:
        reply(self.update, message)

    def disable_pings(self, message: str) -> None:
        # TODO: implement
        return message

    def message_author(self) -> None:
        return self.update.message.from_user.mention_markdown_v2()
