import asyncio

import discord

from src.api.command import ExecutionContext
from src.config import bc


class DiscordExecutionContext(ExecutionContext):
    def __init__(self, message: discord.Message, silent=False) -> None:
        super().__init__()
        self.platform = "discord"
        self.message = message
        self.permission_level = bc.config.users[message.author.id].permission_level
        self.silent = silent

    def send_message(self, message: str) -> None:
        if self.silent:
            return
        asyncio.create_task(self.message.channel.send(message))
