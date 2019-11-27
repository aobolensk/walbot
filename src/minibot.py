import discord
import os
import psutil
import yaml

from .config import runtime_config
from .config import bot_wrapper
from .config import GuildSettings
from .config import User
from .config import Config
from .log import log

config_path = "config.yaml"


class MiniWalBot(discord.Client):
    def __init__(self, config):
        super(MiniWalBot, self).__init__()
        self.config = config

    async def on_ready(self):
        log.info("Logged in as: {} {} (MiniWalBot)".format(self.user.name, self.user.id))
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)
        bot_wrapper.bot_user = self.user

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
            if self.config.users[message.author.id].permission_level < 0:
                return
            if not message.content.startswith(self.config.commands_prefix):
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
    config = None
    try:
        runtime_config.yaml_loader = yaml.CLoader
        log.info("Using fast YAML Loader")
    except Exception:
        runtime_config.yaml_loader = yaml.Loader
        log.info("Using slow YAML Loader")
    try:
        runtime_config.yaml_dumper = yaml.CDumper
        log.info("Using fast YAML Dumper")
    except Exception:
        runtime_config.yaml_dumper = yaml.Dumper
        log.info("Using slow YAML Dumper")
    with open(".bot_cache", 'w') as f:
        f.write(str(os.getpid()))
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            try:
                config = yaml.load(f.read(), Loader=runtime_config.yaml_loader)
            except Exception:
                log.error("yaml.load failed", exc_info=True)
        config.__init__()
    if config is None:
        config = Config()
    miniWalBot = MiniWalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    # Starting mini bot
    miniWalBot.run(config.token)
    # After stopping mini bot
    log.info("Bot is disconnected!")
    os.remove(".bot_cache")
