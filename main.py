import discord
import os
import yaml


class Commands:
    def _get_member_list(self):
        return [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith('_')]

    async def ping(self, message):
        """Check whether the bot is active"""
        await message.channel.send("Pong! " + message.author.mention)

    async def help(self, message):
        """Print list of commands"""
        result = [method_name + ": " + getattr(self, method_name).__doc__
                for method_name in self._get_member_list()
                if getattr(self, method_name).__doc__ is not None]
        await message.channel.send('\n'.join(result))


class Config:

    def __init__(self):
        self.commands = Commands()
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "token"):
            self.token = None


class WalBot(discord.Client):
    def __init__(self, config):
        super(WalBot, self).__init__()
        self.config = config

    async def on_ready(self):
        print("Logged in as: {} {}".format(self.user.name, self.user.id))
        for guild in self.guilds:
            if guild.id not in self.config.guilds:
                self.config.guilds[guild.id] = dict()
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    self.config.guilds[guild.id][channel.id] = None

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!'):
            command = message.content.split(' ')
            command[0] = command[0][1:]
            if command[0] in self.config.commands._get_member_list():
                command_name = self.config.commands._get_member_list()[self.config.commands._get_member_list().index(command[0])]
                await getattr(self.config.commands, command_name)(message)
            else:
                await message.channel.send("Unknown command. !help for more information")


def main():
    config = None
    if os.path.isfile("config.yaml"):
        with open("config.yaml", 'r') as f:
            config = yaml.load(f.read())
        config.__init__()
    if config is None:
        config = Config()
    walBot = WalBot(config)
    if config.token is None:
        config.token = input("Enter your token: ")
    walBot.run(config.token)
    print("Disconnected")
    print(config.guilds)
    with open('config.yaml', 'wb') as f:
        f.write(yaml.dump(config, encoding='utf-8'))

if __name__ == "__main__":
    main()
