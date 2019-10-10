import asyncio
import discord
import logging
import logging.config
import os
import re
import threading
import yaml

from commands import *

log = None


class Reaction:
    def __init__(self, regex, emoji):
        self.regex = regex
        self.emoji = emoji


class GuildSettings:
    def __init__(self, id):
        self.id = id
        self.is_whitelisted = False
        self.whilelist = set()


class User:
    def __init__(self, id):
        self.id = id
        self.permission_level = 0


class Config:
    def __init__(self):
        if not hasattr(self, "commands"):
            self.commands = Commands(self)
        self.commands.update_builtins()
        if not hasattr(self, "reactions"):
            self.reactions = []
        if not hasattr(self, "token"):
            self.token = None
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "users"):
            self.users = dict()
        if not hasattr(self, "commands_prefix"):
            self.commands_prefix = "!"

    def save(self, filename):
        mutex = threading.Lock()
        mutex.acquire()
        log.info("Saving of config is started")
        with open(filename, 'wb') as f:
            try:
                f.write(yaml.dump(self, encoding='utf-8'))
                log.info("Saving of config is finished")
            except Exception:
                log.error("yaml.dump failed", exc_info=True)
        mutex.release()


class WalBot(discord.Client):
    def __init__(self, config):
        global runtime_config
        super(WalBot, self).__init__()
        self.config = config
        self.loop.create_task(self.config_autosave())
        runtime_config.background_loop = self.loop

    async def config_autosave(self):
        await self.wait_until_ready()
        while not self.is_closed():
            self.config.save("config.yaml")
            await asyncio.sleep(10 * 60)

    async def on_ready(self):
        log.info("Logged in as: {} {}".format(self.user.name, self.user.id))
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)

    async def on_message(self, message):
        try:
            log.info(str(message.author) + " -> " + message.content)
            if message.author.id == self.user.id:
                return
            if message.guild.id is None:
                return
            if self.config.guilds[message.guild.id].is_whitelisted:
                if message.channel.id not in self.config.guilds[message.guild.id].whilelist:
                    return
            if message.author.id not in self.config.users.keys():
                self.config.users[message.author.id] = User(message.author.id)
            if not message.content.startswith(self.config.commands_prefix):
                for reaction in self.config.reactions:
                    if re.search(reaction.regex, message.content):
                        log.info("Added reaction " + reaction.emoji)
                        await message.add_reaction(reaction.emoji)
                return
            command = message.content.split(' ')
            command = list(filter(None, command))
            command[0] = command[0][1:]
            if command[0] not in self.config.commands.data.keys():
                await message.channel.send("Unknown command '{}'".format(command[0]))
                return
            actor = self.config.commands.data[command[0]]
            await actor.run(message, command, self.config.users[message.author.id])
        except Exception:
            log.error("on_message failed", exc_info=True)


def setup_logging():
    global log
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
    })
    log = logging.getLogger("WalBot")
    log.setLevel(logging.INFO)
    fh = logging.FileHandler("log.txt")
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(ch)
    log.info("Logging system is set up")


def main():
    setup_logging()
    config = None
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as f:
            try:
                config = yaml.load(f.read(), Loader=yaml.Loader)
            except Exception:
                log.error("yaml.load failed", exc_info=True)
        config.__init__()
    if config is None:
        config = Config()
    runtime_config = RuntimeConfig()
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    walBot.run(config.token)
    for event in runtime_config.background_events:
        event.cancel()
    runtime_config.background_loop = None
    log.info("Bot is disconnected!")
    config.save("config.yaml")


if __name__ == "__main__":
    main()
