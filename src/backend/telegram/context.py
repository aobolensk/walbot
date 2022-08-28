from telegram import Update

from src.api.execution_context import ExecutionContext
from src.backend.telegram.util import escape_markdown_text, reply
from src.config import bc


class TelegramExecutionContext(ExecutionContext):
    def __init__(self, update: Update) -> None:
        super().__init__()
        self.platform = "telegram"
        self.update = update
        self.permission_level = bc.config.telegram.users[update.message.from_user.id].permission_level

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        message = escape_markdown_text(message)
        message = message.replace(
            escape_markdown_text("@__telegram_message_author@"),
            self.update.message.from_user.mention_markdown_v2())
        reply(
            self.update, message,
            disable_web_page_preview=kwargs.get("suppress_embeds", False),
        )

    def disable_pings(self, message: str) -> None:
        # TODO: implement
        return message

    def message_author(self) -> None:
        return "@__telegram_message_author@"
