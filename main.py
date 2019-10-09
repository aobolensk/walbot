import discord
import logging
import logging.config
import os
import re
import yaml

from commands import *

log = None
COMMANDS_PREFIX = '!'

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
        if not hasattr(self, "reactions"):
            self.reactions = []
        self.commands.update_builtins()
        if not hasattr(self, "token"):
            self.token = None
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "users"):
            self.users = dict()


class WalBot(discord.Client):
    def __init__(self, config):
        super(WalBot, self).__init__()
        self.config = config

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
            if not message.content.startswith(COMMANDS_PREFIX):
                for reaction in self.config.reactions:
                    if re.search(reaction.regex, message.content):
                        log.info("Added reaction " + reaction.emoji)
                        await message.add_reaction(reaction.emoji)
                return
            command = message.content.split(' ')
            command[0] = command[0][1:]
            if command[0] not in self.config.commands.data.keys():
                await message.channel.send("Unknown command '{}'".format(command[0]))
                return
            actor = self.config.commands.data[command[0]]
            if not actor.is_available(message.channel.id):
                await message.channel.send("Command '{}' is not available in this channel".format(command[0]))
                return
            if actor.permission > self.config.users[message.author.id].permission_level:
                await message.channel.send("You don't have permission to call command '{}'".format(command[0]))
                return
            if actor.perform is not None:
                await self.config.commands.data[command[0]].perform(message, command)
            elif actor.message is not None:
                respond = actor.message
                respond = respond.replace("@author@", message.author.mention)
                respond = respond.replace("@args@", ' '.join(command[1:]))
                for i in range(len(command)):
                    respond = respond.replace("@arg" + str(i) + "@", command[i])
                if (len(respond.strip()) > 0):
                    await message.channel.send(respond)
            else:
                await message.channel.send("Command '{}' is not callable".format(command[0]))
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
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    walBot.run(config.token)
    log.info("Bot is disconnected!")
    with open('config.yaml', 'wb') as f:
        try:
            f.write(yaml.dump(config, encoding='utf-8'))
        except Exception:
            log.error("yaml.dump failed", exc_info=True)


if __name__ == "__main__":
    main()
