import asyncio
import discord
import os
import re
import yaml

from config import runtime_config
from config import log
from config import GuildSettings
from config import User
from config import Config


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


def main():
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
    for event in runtime_config.background_events:
        event.cancel()
    runtime_config.background_loop = None
    log.info("Bot is disconnected!")
    config.save("config.yaml")


if __name__ == "__main__":
    main()
