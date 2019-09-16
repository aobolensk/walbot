import discord
import os
import yaml


class Commands:
    def __init__(self, config):
        self.config = config

    def _get_all_commands(self):
        return [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith('_')]

    def _get_available_commands(self, message):
        result = []
        for func in self._get_all_commands():
            if (func in self.config.available_commands or
                (message.channel.guild.id in self.config.guilds and
                message.channel.id in self.config.guilds[message.channel.guild.id] and
                func in self.config.guilds[message.channel.guild.id][message.channel.id]["available_commands"])):
                result.append(func)
        result.sort()
        return result

    async def ping(self, message):
        """Check whether the bot is active"""
        await message.channel.send("Pong! " + message.author.mention)

    async def help(self, message):
        """Print list of commands"""
        result = [method_name + ": " + getattr(self, method_name).__doc__
                for method_name in self._get_available_commands(message)
                if getattr(self, method_name).__doc__ is not None]
        await message.channel.send('\n'.join(result))


class Config:
    def __init__(self):
        self.commands = Commands(self)
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "token"):
            self.token = None
        if not hasattr(self, "available_commands"):
            self.available_commands = {
                "ping",
                "help"
            }


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
                if channel.id not in self.config.guilds[guild.id]:
                    if isinstance(channel, discord.TextChannel):
                        self.config.guilds[guild.id][channel.id] = {
                            "available_commands": set()
                        }

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!'):
            command = message.content.split(' ')
            command[0] = command[0][1:]
            if command[0] in self.config.commands._get_available_commands(message):
                command_name = (self.config.commands._get_available_commands(message)
                    [self.config.commands._get_available_commands(message).index(command[0])])
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
