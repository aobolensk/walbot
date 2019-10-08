import discord
import os
import re
import yaml

from commands import *


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
        print("Logged in as: {} {}".format(self.user.name, self.user.id))
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        if self.config.guilds[message.guild.id].is_whitelisted:
            if message.channel.id not in self.config.guilds[message.guild.id].whilelist:
                return
        if message.author.id not in self.config.users.keys():
            self.config.users[message.author.id] = User(message.author.id)
        for reaction in self.config.reactions:
            if re.search(reaction.regex, message.content):
                await message.add_reaction(reaction.emoji)
        if message.content.startswith('!'):
            command = message.content.split(' ')
            command[0] = command[0][1:]
            if command[0] in self.config.commands.data.keys():
                actor = self.config.commands.data[command[0]]
                if actor.is_available(message.channel.id):
                    if actor.permission <= self.config.users[message.author.id].permission_level:
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
                    else:
                        await message.channel.send("You don't have permission to call command '{}'".format(command[0]))
                else:
                    await message.channel.send("Command '{}' is not available in this channel".format(command[0]))
            else:
                await message.channel.send("Unknown command '{}'".format(command[0]))


def main():
    config = None
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as f:
            config = yaml.load(f.read(), Loader=yaml.Loader)
        config.__init__()
    if config is None:
        config = Config()
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    walBot.run(config.token)
    print("Disconnected")
    with open('config.yaml', 'wb') as f:
        f.write(yaml.dump(config, encoding='utf-8'))

if __name__ == "__main__":
    main()
