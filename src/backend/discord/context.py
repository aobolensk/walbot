import asyncio
import re

import discord

from src import const
from src.api.command import ExecutionContext
from src.backend.discord.message import Msg
from src.config import bc


class DiscordExecutionContext(ExecutionContext):
    def __init__(self, message: discord.Message, silent=False) -> None:
        super().__init__()
        self.platform = "discord"
        self.message = message
        self.permission_level = bc.config.users[message.author.id].permission_level
        self.silent = silent

    def send_message(self, message: str, *args, **kwargs) -> None:
        t = asyncio.create_task(Msg.response(self.message, message, self.silent, *args, **kwargs))
        return asyncio.run(t)

    def disable_pings(self, message: str) -> None:
        while True:
            r = const.USER_ID_REGEX.search(message)
            if r is None:
                break
            t = asyncio.create_task(self.message.guild.fetch_member(int(r.group(1))))
            member = asyncio.run(t)
            message = const.USER_ID_REGEX.sub(str(member), message, count=1)
        while True:
            r = const.ROLE_ID_REGEX.search(message)
            if r is None:
                break
            for role in message.guild.roles:
                if str(role.id) == r.group(1):
                    message = const.ROLE_ID_REGEX.sub(f"`{role.name}`", message, count=1)
                    break
        message = re.sub(const.ROLE_EVERYONE, "`" + const.ROLE_EVERYONE + "`", message)
        message = re.sub(const.ROLE_HERE, "`" + const.ROLE_HERE + "`", message)
        return message
