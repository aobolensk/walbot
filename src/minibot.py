import discord
import os
import psutil
import yaml

from . import const
from .config import Config
from .config import GuildSettings
from .config import SecretConfig
from .config import User
from .config import bc
from .log import log


class MiniWalBot(discord.Client):
    def __init__(self, config, secret_config):
        super(MiniWalBot, self).__init__()
        self.config = config
        self.secret_config = secret_config

    async def on_ready(self):
        log.info("Logged in as: {} {} ({})".format(self.user.name, self.user.id, self.__class__.__name__))
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)

    async def on_message(self, message):
        try:
            log.info(str(message.author) + " -> " + message.content)
            if message.author.id == self.user.id:
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
            if (not message.content.startswith(self.config.commands_prefix) and
               not self.user.mentioned_in(message)):
                return
            await message.channel.send("<Maintenance break>")
        except Exception:
            log.error("on_message failed", exc_info=True)


def start():
    if os.path.exists(".bot_cache"):
        cache = None
        with open(".bot_cache", 'r') as f:
            cache = f.read()
        if cache is not None:
            pid = int(cache)
            if psutil.pid_exists(pid):
                print("Bot is already running!")
                return
    # Before starting mini bot
    secret_config = None
    config = None
    try:
        bc.yaml_loader = yaml.CLoader
        log.info("Using fast YAML Loader")
    except Exception:
        bc.yaml_loader = yaml.Loader
        log.info("Using slow YAML Loader")
    try:
        bc.yaml_dumper = yaml.CDumper
        log.info("Using fast YAML Dumper")
    except Exception:
        bc.yaml_dumper = yaml.Dumper
        log.info("Using slow YAML Dumper")
    with open(".bot_cache", 'w') as f:
        f.write(str(os.getpid()))
    if os.path.isfile(const.CONFIG_PATH):
        with open(const.CONFIG_PATH, 'r') as f:
            try:
                config = yaml.load(f.read(), Loader=bc.yaml_loader)
            except Exception:
                log.error("yaml.load failed on file: {}".format(const.CONFIG_PATH), exc_info=True)
        config.__init__()
    if config is None:
        config = Config()
    if os.path.isfile(const.SECRET_CONFIG_PATH):
        with open(const.SECRET_CONFIG_PATH, 'r') as f:
            try:
                secret_config = yaml.load(f.read(), Loader=bc.yaml_loader)
            except Exception:
                log.error("yaml.load failed on file: {}".format(const.SECRET_CONFIG_PATH), exc_info=True)
        secret_config.__init__()
    if secret_config is None:
        secret_config = SecretConfig()
    miniWalBot = MiniWalBot(config, secret_config)
    if secret_config.token is None:
        secret_config.token = input("Enter your token: ")
    # Starting mini bot
    miniWalBot.run(secret_config.token)
    # After stopping mini bot
    log.info("Bot is disconnected!")
    os.remove(".bot_cache")
