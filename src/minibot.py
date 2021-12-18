import discord

from src import const
from src.config import Config, GuildSettings, SecretConfig, User
from src.log import log


class MiniWalBot(discord.Client):
    def __init__(self, name: str, config: Config, secret_config: SecretConfig, bot_response: str) -> None:
        super().__init__()
        self.repl = None
        self.instance_name = name
        self.config = config
        self.secret_config = secret_config
        self.bot_response = bot_response

    async def on_ready(self) -> None:
        log.info(
            f"Logged in as: {self.user.name} {self.user.id} ({self.__class__.__name__}), "
            f"instance: {self.instance_name}")
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)

    async def on_message(self, message: discord.Message) -> None:
        try:
            if self.config.guilds[message.channel.guild.id].ignored:
                return
            log.info(str(message.author) + " -> " + message.content)
            if message.author.id == self.user.id:
                return
            if isinstance(message.channel, discord.DMChannel):
                return
            if message.channel.guild.id is None:
                return
            if self.config.guilds[message.channel.guild.id].is_whitelisted:
                if message.channel.id not in self.config.guilds[message.channel.guild.id].whitelist:
                    return
            if message.author.id not in self.config.users.keys():
                self.config.users[message.author.id] = User(message.author.id)
            if self.config.users[message.author.id].permission_level < const.Permission.USER.value:
                return
            if not message.content.startswith(self.config.commands_prefix) and not self.user.mentioned_in(message):
                return
            await message.channel.send(self.bot_response)
        except Exception:
            log.error("on_message failed", exc_info=True)
