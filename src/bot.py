import asyncio
import datetime
import discord
import os
import psutil
import signal
import time
import re
import yaml

from . import const
from .config import bc
from .config import GuildSettings
from .config import User
from .config import Config
from .config import SecretConfig
from .log import log
from .markov import Markov


class WalBot(discord.Client):
    def __init__(self, config, secret_config):
        super(WalBot, self).__init__()
        self.config = config
        self.secret_config = secret_config
        self.loop.create_task(self.config_autosave())
        self.loop.create_task(self.process_reminders())
        bc.config = self.config
        bc.commands = self.config.commands
        bc.background_loop = self.loop
        bc.change_status = self.change_status
        bc.change_presence = self.change_presence
        bc.get_channel = self.get_channel
        bc.close = self.close
        bc.secret_config = self.secret_config
        if not os.path.exists(const.markov_path):
            bc.markov = Markov()
        else:
            with open(const.markov_path, 'rb') as f:
                try:
                    bc.markov = yaml.load(f.read(), Loader=bc.yaml_loader)
                except Exception:
                    log.error("yaml.load failed on file: {}".format(const.markov_path), exc_info=True)
        if bc.markov.check():
            log.info("Markov model has passed all checks")
        else:
            log.info("Markov model has not passed checks, but all errors were fixed")

    async def change_status(self, string, type):
        await self.change_presence(activity=discord.Activity(name=string, type=type))

    async def config_autosave(self):
        await self.wait_until_ready()
        index = 1
        while not self.is_closed():
            if index % 10 == 0:
                self.config.backup(const.config_path, const.markov_path)
            self.config.save(const.config_path, const.markov_path, const.secret_config_path)
            index += 1
            await asyncio.sleep(10 * 60)

    async def process_reminders(self):
        await self.wait_until_ready()
        while not self.is_closed():
            now = datetime.datetime.now().replace(second=0).strftime(const.REMINDER_TIME_FORMAT)
            i = 0
            while i < len(self.config.reminders):
                rem = self.config.reminders[i]
                if rem == now:
                    channel = self.get_channel(rem.channel_id)
                    await channel.send("You asked to remind at {} -> {}".format(now, rem.message))
                    self.config.reminders.pop(i)
                elif rem < now:
                    self.config.reminders.pop(i)
                else:
                    i += 1
            await asyncio.sleep(30)

    async def on_ready(self):
        log.info("Logged in as: {} {} ({})".format(self.user.name, self.user.id, self.__class__.__name__))
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)
        bc.bot_user = self.user

    async def on_message(self, message):
        try:
            log.info("<" + str(message.id) + "> " + str(message.author) + " -> " + message.content)
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
            if self.config.users[message.author.id].permission_level < 0:
                return
            if message.content.startswith(self.config.commands_prefix):
                await self.process_command(message)
            else:
                await self.process_regular_message(message)
        except Exception:
            log.error("on_message failed", exc_info=True)

    async def process_regular_message(self, message):
        if bc.bot_user.mentioned_in(message):
            if message.channel.id in self.config.guilds[message.channel.guild.id].responses_whitelist:
                await message.channel.send(message.author.mention + ' ' + bc.markov.generate())
        elif message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
            bc.markov.add_string(message.content)
        if message.channel.id not in self.config.guilds[message.channel.guild.id].reactions_whitelist:
            return
        for reaction in self.config.reactions:
            if re.search(reaction.regex, message.content):
                log.info("Added reaction " + reaction.emoji)
                try:
                    await message.add_reaction(reaction.emoji)
                except discord.HTTPException:
                    pass

    async def process_command(self, message):
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

    async def on_raw_message_edit(self, payload):
        try:
            log.info("<" + str(payload.message_id) + "> (edit) " +
                     payload.data["author"]["username"] + "#" + payload.data["author"]["discriminator"] +
                     " -> " + payload.data["content"])
        except KeyError:
            pass

    async def on_raw_message_delete(self, payload):
        log.info("<" + str(payload.message_id) + "> (delete)")


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
    # Before starting the bot
    config = None
    secret_config = None
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
    if os.path.isfile(const.config_path):
        with open(const.config_path, 'r') as f:
            try:
                config = yaml.load(f.read(), Loader=bc.yaml_loader)
            except Exception:
                log.error("yaml.load failed on file: {}".format(const.config_path), exc_info=True)
        config.__init__()
    if config is None:
        config = Config()
    if os.path.isfile(const.secret_config_path):
        with open(const.secret_config_path, 'r') as f:
            try:
                secret_config = yaml.load(f.read(), Loader=bc.yaml_loader)
            except Exception:
                log.error("yaml.load failed on file: {}".format(const.secret_config_path), exc_info=True)
        secret_config.__init__()
    if secret_config is None:
        secret_config = SecretConfig()
    walBot = WalBot(config, secret_config)
    if secret_config.token is None:
        secret_config.token = input("Enter your token: ")
    # Starting the bot
    walBot.run(secret_config.token)
    # After stopping the bot
    for event in bc.background_events:
        event.cancel()
    bc.background_loop = None
    log.info("Bot is disconnected!")
    config.save(const.config_path, const.markov_path, const.secret_config_path, wait=True)
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
    if psutil.pid_exists(pid):
        os.kill(pid, signal.SIGINT)
        while True:
            is_running = psutil.pid_exists(pid)
            if not is_running:
                break
            print("Bot is still running. Please, wait...")
            time.sleep(0.5)
        print("Bot is stopped!")
    else:
        print("Could not stop the bot (bot is not running)")
