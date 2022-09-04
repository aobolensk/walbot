from telegram import Update

from src import const
from src.api.execution_context import ExecutionContext
from src.backend.telegram.util import escape_markdown_text, reply
from src.config import bc


class TelegramExecutionContext(ExecutionContext):
    def __init__(self, update: Update) -> None:
        super().__init__()
        self.platform = "telegram"
        self.update = update
        self.permission_level = bc.config.telegram.users[update.message.from_user.id].permission_level
        self._replace_patterns = dict()

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        message = self._unescape_ping1(message)
        message = escape_markdown_text(message)
        message = self._unescape_ping2(message)
        reply(
            self.update, message,
            disable_web_page_preview=kwargs.get("suppress_embeds", False),
            reply_on_msg=kwargs.get("reply_on_msg", False),
        )

    async def reply(self, message: str, *args, **kwargs) -> None:
        await self.send_message(message, *args, **kwargs, reply_on_msg=True)

    def _unescape_ping1(self, message: str) -> str:
        idx = 0
        while True:
            r = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.search(message)
            if r is None:
                break
            message = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.sub(f"@__telegram_message_author_{idx}@", message)
            self._replace_patterns[f"@__telegram_message_author_{idx}@"] = r.group(0)
            idx += 1
        return message

    def _unescape_ping2(self, message: str) -> str:
        for key, value in self._replace_patterns.items():
            message = message.replace(escape_markdown_text(key), value)
        return message

    def disable_pings(self, message: str) -> str:
        while True:
            r = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.search(message)
            if r is None:
                break
            message = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.sub(r.groups()[0], message)
        return message

    def message_author(self) -> str:
        return self.update.message.from_user.mention_markdown_v2()

    def message_author_id(self) -> str:
        return self.update.message.from_user.id

    def channel_name(self) -> str:
        return self.update.message.chat.title or "<DM>"

    def channel_id(self) -> int:
        return self.update.message.chat.id
