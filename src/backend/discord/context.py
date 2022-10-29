import asyncio
import re
from typing import Optional

import discord

from src import const
from src.api.execution_context import ExecutionContext
from src.backend.discord.message import Msg
from src.config import bc


class DiscordExecutionContext(ExecutionContext):
    def __init__(self, message: discord.Message, silent=False) -> None:
        super().__init__()
        self.platform = "discord"
        self.message = message
        self.permission_level = bc.config.discord.users[message.author.id].permission_level
        self.silent = silent

    async def send_message(self, message: str, *args, **kwargs) -> Optional[discord.Message]:
        if "files" in kwargs:
            kwargs["files"] = [discord.File(x) for x in kwargs["files"]]
        return await Msg.response(self.message, message, self.silent, *args, **kwargs)

    async def reply(self, message: str, *args, **kwargs) -> Optional[discord.Message]:
        if "files" in kwargs:
            kwargs["files"] = [discord.File(x) for x in kwargs["files"]]
        return await Msg.reply(self.message, message, self.silent, *args, **kwargs)

    async def send_direct_message(self, user_id: int, message: str, *args, **kwargs) -> Optional[discord.Message]:
        if "files" in kwargs:
            kwargs["files"] = [discord.File(x) for x in kwargs["files"]]
        return await Msg.send_direct_message(bc.discord.get_user(user_id), message, self.silent, *args, **kwargs)

    def disable_pings(self, message: str) -> str:
        while True:
            r = const.DISCORD_USER_ID_REGEX.search(message)
            if r is None:
                break
            t = asyncio.create_task(self.message.guild.fetch_member(int(r.group(1))))
            member = asyncio.run(t)
            message = const.DISCORD_USER_ID_REGEX.sub(str(member), message, count=1)
        while True:
            r = const.DISCORD_ROLE_ID_REGEX.search(message)
            if r is None:
                break
            for role in message.guild.roles:
                if str(role.id) == r.group(1):
                    message = const.DISCORD_ROLE_ID_REGEX.sub(f"`{role.name}`", message, count=1)
                    break
        message = re.sub(const.ROLE_EVERYONE, "`" + const.ROLE_EVERYONE + "`", message)
        message = re.sub(const.ROLE_HERE, "`" + const.ROLE_HERE + "`", message)
        return message

    def message_author(self) -> str:
        return self.message.author.mention

    def message_author_id(self) -> int:
        return self.message.author.id

    def channel_name(self) -> str:
        return self.message.channel.mention

    def channel_id(self) -> int:
        return self.message.channel.id
