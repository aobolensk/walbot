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

    async def ping(self, message, command):
        """Check whether the bot is active"""
        await message.channel.send("Pong! " + message.author.mention)

    async def help(self, message, command):
        """Print list of commands"""
        result = [method_name + ": " + getattr(self, method_name).__doc__
                for method_name in self._get_available_commands(message)
                if getattr(self, method_name).__doc__ is not None]
        await message.channel.send('\n'.join(result))

    async def cmd(self, message, command):
        """Commands settings: !cmd <command_name> <option> <value> <scope>"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'cmd'")
        else:
            command_name = command[1]
            option = command[2]
            value = command[3]
            scope = command[4] if len(command) >= 5 else "channel"
            if command_name not in self._get_all_commands():
                await message.channel.send("Unknown command: " + command_name)
                return
            if scope not in ("channel", "guild", "global"):
                await message.channel.send("Unknown scope: " + scope)
                return
            if option == "enable":
                if value == "on":
                    if scope == "channel":
                        self.config.guilds[message.channel.guild.id][message.channel.id]["available_commands"].add(command_name)
                    elif scope == "guild":
                        for channel in self.config.guilds[message.channel.guild.id]:
                            self.config.guilds[message.channel.guild.id][channel]["available_commands"].add(command_name)
                    elif scope == "global":
                        self.config.available_commands.add(command_name)
                    await message.channel.send("Successfully enabled command {} in scope {}".format(command_name, scope))
                elif value == "off":
                    if scope == "channel":
                        self.config.guilds[message.channel.guild.id][message.channel.id]["available_commands"].discard(command_name)
                    elif scope == "guild":
                        for channel in self.config.guilds[message.channel.guild.id]:
                            self.config.guilds[message.channel.guild.id][channel]["available_commands"].discard(command_name)
                    elif scope == "global":
                        self.config.available_commands.discard(command_name)
                    await message.channel.send("Successfully disabled command {} in scope {}".format(command_name, scope))
                else:
                    await message.channel.send("Unknown value: " + value)
                    return
            else:
                await message.channel.send("Unknown option: " + option)
                return


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
                "help",
                "cmd"
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
                await getattr(self.config.commands, command_name)(message, command)
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
