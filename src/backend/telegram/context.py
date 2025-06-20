import os
from typing import Dict

from telegram import Update
from telegram.ext import CallbackContext

from src import const
from src.api.execution_context import ExecutionContext
from src.backend.telegram.util import escape_markdown_text, reply, send_message
from src.config import bc
from src.utils import Util


class TelegramExecutionContext(ExecutionContext):
    def __init__(self, update: Update, context: CallbackContext) -> None:
        super().__init__()
        self.platform = str(const.BotBackend.TELEGRAM)
        self.update = update
        self.context = context
        self.user = bc.config.telegram.users[update.message.from_user.id]
        self.permission_level = bc.config.telegram.users[update.message.from_user.id].permission_level
        self._replace_patterns: Dict[str, str] = dict()

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        message = message or ""
        message = self._unescape_ping1(message)
        message = escape_markdown_text(message)
        message = self._unescape_ping2(message)
        for idx, chunk in enumerate(Util.split_by_chunks(message, const.TELEGRAM_MAX_MESSAGE_LENGTH)):
            await reply(
                self.update, chunk,
                disable_web_page_preview=kwargs.get("suppress_embeds", False),
                reply_on_msg=kwargs.get("reply_on_msg", False),
            )
            if idx == 0:
                if "files" in kwargs:
                    for file in kwargs["files"]:
                        await self._send_file(file)

    async def _send_file(self, file_path: str) -> None:
        await self.update.message.reply_document(open(file_path, 'rb'), os.path.basename(file_path))

    async def reply(self, message: str, *args, **kwargs) -> None:
        await self.send_message(message, *args, **kwargs, reply_on_msg=True)

    async def send_direct_message(self, user_id: int, message: str, *args, **kwargs) -> None:
        send_message(user_id, message)

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

    async def disable_pings(self, message: str) -> str:
        while True:
            r = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.search(message)
            if r is None:
                break
            message = const.TELEGRAM_MARKDOWN_V2_MENTION_REGEX.sub(r.groups()[0], message)
        return message

    def message_author(self) -> str:
        return self.update.message.from_user.mention_markdown_v2()

    def message_author_id(self) -> str:
        return str(self.update.message.from_user.id)

    def channel_name(self) -> str:
        return self.update.message.chat.title or "<DM>"

    def channel_id(self) -> int:
        return self.update.message.chat.id

    def bot_user_id(self) -> int:
        return 0
