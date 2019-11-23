import asyncio
import discord
import os
import psutil
import signal
import time
import re
import yaml

from .config import runtime_config
from .config import bot_wrapper
from .config import GuildSettings
from .config import User
from .config import Config
from .log import log
from .markov import Markov


class WalBot(discord.Client):
    def __init__(self, config):
        global runtime_config
        super(WalBot, self).__init__()
        self.config = config
        self.loop.create_task(self.config_autosave())
        bot_wrapper.background_loop = self.loop
        bot_wrapper.change_status = self.change_status
        bot_wrapper.get_channel = self.get_channel
        if not os.path.exists("markov.yaml"):
            runtime_config.markov = Markov()
        else:
            with open("markov.yaml", 'rb') as f:
                runtime_config.markov = yaml.load(f.read(), Loader=runtime_config.yaml_loader)

    async def change_status(self, string, type):
        await self.change_presence(activity=discord.Activity(name=string, type=type))

    async def config_autosave(self):
        await self.wait_until_ready()
        index = 1
        while not self.is_closed():
            self.config.save("config.yaml", "markov.yaml")
            if index % 10 == 0:
                self.config.backup("config.yaml", "markov.yaml")
            index += 1
            await asyncio.sleep(10 * 60)

    async def on_ready(self):
        log.info("Logged in as: {} {}".format(self.user.name, self.user.id))
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
                if (bot_wrapper.bot_user.mentioned_in(message) and
                        self.config.commands.data["markov"].is_available(message.channel.id)):
                    await message.channel.send(message.author.mention + ' ' + runtime_config.markov.generate())
                elif message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                    runtime_config.markov.add_string(message.content)
                if message.channel.id not in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                    return
                for reaction in self.config.reactions:
                    if re.search(reaction.regex, message.content):
                        log.info("Added reaction " + reaction.emoji)
                        try:
                            await message.add_reaction(reaction.emoji)
                        except discord.HTTPException:
                            pass
                return
            command = message.content.split(' ')
            command = list(filter(None, command))
            command[0] = command[0][1:]
            if len(command[0]) == 0:
                log.debug("Ignoring empty command")
                return
            if command[0] not in self.config.commands.data.keys():
                if command[0] in self.config.commands.aliases.keys():
                    command[0] = self.config.commands.aliases[command[0]]
                else:
                    await message.channel.send("Unknown command '{}'".format(command[0]))
                    return
            actor = self.config.commands.data[command[0]]
            await actor.run(message, command, self.config.users[message.author.id])
        except Exception:
            log.error("on_message failed", exc_info=True)


def start():
    # Before starting the bot
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
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as f:
            try:
                config = yaml.load(f.read(), Loader=runtime_config.yaml_loader)
            except Exception:
                log.error("yaml.load failed", exc_info=True)
        config.__init__()
    if config is None:
        config = Config()
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    # Starting the bot
    walBot.run(config.token)
    # After stopping the bot
    for event in runtime_config.background_events:
        event.cancel()
    bot_wrapper.background_loop = None
    log.info("Bot is disconnected!")
    config.save("config.yaml", "markov.yaml", wait=True)
    os.remove(".bot_cache")


def stop():
    cache = None
    if not os.path.exists(".bot_cache"):
        print("Could not stop the bot (cache file does not exist)")
        return
    with open(".bot_cache", 'r') as f:
        cache = f.read()
    if cache is None:
        print("Could not stop the bot (cache file does not contain pid)")
        return
    pid = int(cache)
    os.kill(pid, signal.SIGINT)
    while True:
        is_running = psutil.pid_exists(pid)
        if not is_running:
            break
        print("Bot is still running. Please, wait...")
        time.sleep(0.5)
    print("Bot is stopped!")
