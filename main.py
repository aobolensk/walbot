import discord
import os
import re
import yaml


class Command:
    def __init__(self, name, perform=None, message=None, permission=0):
        self.name = name
        self.perform = perform
        self.permission = permission
        self.message = message
        self.is_global = False
        self.channels = []

    def is_available(self, channel_id):
        return self.is_global or (channel_id in self.channels)


class Commands:
    def __init__(self, config):
        self.config = config
        self.data = dict()

    def update_builtins(self):
        if "ping" not in self.data.keys():
            self.data["ping"] = Command("ping",
                perform=self._ping, permission=0)
            self.data["ping"].is_global = True
        if "help" not in self.data.keys():
            self.data["help"] = Command("help",
                perform=self._help, permission=0)
            self.data["help"].is_global = True
        if "addcmd" not in self.data.keys():
            self.data["addcmd"] = Command("addcmd",
                perform=self._addcmd, permission=1)
            self.data["addcmd"].is_global = True
        if "updcmd" not in self.data.keys():
            self.data["updcmd"] = Command("updcmd",
                perform=self._updcmd, permission=1)
            self.data["updcmd"].is_global = True
        if "delcmd" not in self.data.keys():
            self.data["delcmd"] = Command("delcmd",
                perform=self._delcmd, permission=1)
            self.data["delcmd"].is_global = True
        if "enablecmd" not in self.data.keys():
            self.data["enablecmd"] = Command("enablecmd",
                perform=self._enablecmd, permission=1)
            self.data["enablecmd"].is_global = True
        if "disablecmd" not in self.data.keys():
            self.data["disablecmd"] = Command("disablecmd",
                perform=self._disablecmd, permission=1)
            self.data["disablecmd"].is_global = True
        if "whitelist" not in self.data.keys():
            self.data["whitelist"] = Command("whitelist",
                perform=self._whitelist, permission=1)
            self.data["whitelist"].is_global = True
        if "addreaction" not in self.data.keys():
            self.data["addreaction"] = Command("addreaction",
                perform=self._addreaction, permission=1)
            self.data["addreaction"].is_global = True
        if "delreaction" not in self.data.keys():
            self.data["delreaction"] = Command("delreaction",
                perform=self._delreaction, permission=1)
            self.data["delreaction"].is_global = True
        if "listreaction" not in self.data.keys():
            self.data["listreaction"] = Command("listreaction",
                perform=self._listreaction, permission=0)
            self.data["listreaction"].is_global = True
        if "wme" not in self.data.keys():
            self.data["wme"] = Command("wme",
                perform=self._wme, permission=1)
            self.data["wme"].is_global = True


    async def _ping(self, message, command):
        """Check whether the bot is active"""
        await message.channel.send("Pong! " + message.author.mention)

    async def _help(self, message, command):
        """Print list of commands and get examples
        Examples:
                !help
                !help help"""
        result = ""
        if len(command) == 1:
            for command in self.data:
                command = self.data[command]
                result += command.name + ": "
                if command.perform is not None:
                    result += command.perform.__doc__.split('\n')[0]
                else:
                    result += command.message
                result += '\n'
            await message.channel.send(result)
        elif len(command) == 2:
            if command[1] in self.data:
                command = self.data[command[1]]
            result += command.name + ": "
            if command.perform is not None:
                result += command.perform.__doc__
            else:
                result += command.message
            result += '\n'
            await message.channel.send(result)
        else:
            await message.channel.send("Too many arguments for command 'help'")

    async def _addcmd(self, message, command):
        """Add command
        Example: !addcmd hello Hello!"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'addcmd'")
            return
        command_name = command[1]
        if command_name in self.data.keys():
            await message.channel.send("Command {} already exists".format(command_name))
            return
        self.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        self.data[command_name].channels.append(message.channel.id)
        await message.channel.send("Command '{}' -> '{}' successfully added".format(command_name, self.data[command_name].message))

    async def _updcmd(self, message, command):
        """Update command (works only for commands that already exist)
        Example: !updcmd hello Hello!"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'updcmd'")
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if self.data[command_name].message is None:
                await message.channel.send("Command '{}' is not editable".format(command_name))
                return
            self.data[command_name].message = ' '.join(command[2:])
            await message.channel.send("Command '{}' -> '{}' successfully updated".format(command_name, self.data[command_name].message))
            return
        await message.channel.send("Command '{}' does not exist".format(command_name))

    async def _delcmd(self, message, command):
        """Delete command
        Example: !delcmd hello"""
        if len(command) < 2:
            await message.channel.send("Too few arguments for command 'delcmd'")
            return
        if len(command) > 2:
            await message.channel.send("Too many arguments for command 'delcmd'")
            return
        command_name = command[1]
        if command_name in self.data.keys():
            self.data.pop(command_name, None)
            await message.channel.send("Command '{}' -> '{}' successfully deleted".format(command_name))
            return
        await message.channel.send("Command '{}' does not exist".format(command_name))

    async def _enablecmd(self, message, command):
        """Enable command in specified scope
        Examples:
                !enablecmd hello channel
                !enablecmd hello guild
                !enablecmd hello global"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'enablecmd'")
            return
        if len(command) > 3:
            await message.channel.send("Too many arguments for command 'enablecmd'")
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                self.data[command_name].channels.append(message.channel.id)
                await message.channel.send("Command '{}' is enabled in this channel".format(command_name))
            elif command[2] == "guild":
                for channel in message.guild.text_channels:
                    if channel.id not in self.data[command_name].channels:
                        self.data[command_name].channels.append(channel.id)
                await message.channel.send("Command '{}' is enabled in this guild".format(command_name))
            elif command[2] == "global":
                self.data[command_name].is_global = True
                await message.channel.send("Command '{}' is enabled in global scope".format(command_name))
            else:
                await message.channel.send("Unknown scope '{}'".format(command[2]))
            return
        await message.channel.send("Command '{}' does not exist".format(command_name))

    async def _disablecmd(self, message, command):
        """Disable command in specified scope
        Examples:
                !disablecmd hello channel
                !disablecmd hello guild
                !disablecmd hello global"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'disablecmd'")
            return
        if len(command) > 3:
            await message.channel.send("Too many arguments for command 'disablecmd'")
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                if message.channel.id in self.data[command_name].channels:
                    self.data[command_name].channels.remove(message.channel.id)
                await message.channel.send("Command '{}' is disabled in this channel".format(command_name))
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in self.data[command_name].channels:
                        self.data[command_name].channels.remove(channel.id)
                await message.channel.send("Command '{}' is disabled in this guild".format(command_name))
            elif command[2] == "global":
                self.data[command_name].is_global = False
                await message.channel.send("Command '{}' is disabled in global scope".format(command_name))
            else:
                await message.channel.send("Unknown scope '{}'".format(command[2]))
            return
        await message.channel.send("Command '{}' does not exist".format(command_name))

    async def _whitelist(self, message, command):
        """Bot's whitelist
        Examples:
                !whitelist enable/disable
                !whitelist add
                !whitelist remove"""
        if len(command) < 2:
            await message.channel.send("Too few arguments for command 'whitelist'")
            return
        if len(command) > 2:
            await message.channel.send("Too many arguments for command 'whitelist'")
            return
        if command[1] == "enable":
            self.config.guilds[message.guild.id].is_whitelisted = True
            await message.channel.send("This guild is whitelisted for bot")
        elif command[1] == "disable":
            self.config.guilds[message.guild.id].is_whitelisted = False
            await message.channel.send("This guild is not whitelisted for bot")
        elif command[1] == "add":
            self.config.guilds[message.guild.id].whilelist.add(message.channel.id)
            await message.channel.send("This channel is added to bot's whitelist")
        elif command[1] == "remove":
            self.config.guilds[message.guild.id].whilelist.discard(message.channel.id)
            await message.channel.send("This channel is removed from bot's whitelist")
        else:
            await message.channel.send("Unknown argument '{}'".format(command[1]))

    async def _addreaction(self, message, command):
        """Add reaction
        Example: !addreaction emoji regex"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'addreaction'")
            return
        self.config.reactions.append(Reaction(' '.join(command[2:]), command[1]))
        await message.channel.send("Reaction '{}' on '{}' successfully added".format(command[1], ' '.join(command[2:])))

    async def _delreaction(self, message, command):
        """Delete reaction
        Example: !delreaction emoji"""
        if len(command) < 2:
            await message.channel.send("Too few arguments for command 'delreaction'")
            return
        if len(command) > 2:
            await message.channel.send("Too many arguments for command 'delreaction'")
            return
        i = 0
        while i < len(self.config.reactions):
            if self.config.reactions[i].emoji == command[1]:
                self.config.reactions.pop(i)
            else:
                i += 1
        await message.channel.send("Reaction '{}' successsfully removed".format(command[1]))

    async def _listreaction(self, message, command):
        """Show list of reactions
        Example: !listreaction"""
        result = ""
        for reaction in self.config.reactions:
            result += reaction.emoji + ": " + reaction.regex + '\n'
        if len(result) > 0:
            await message.channel.send(result)

    async def _wme(self, message, command):
        """Send direct message to author with something"""
        if message.author.dm_channel is None:
            print("DMChannel is not created")
            await message.author.create_dm()
        if len(message.content) > 0:
            await message.author.dm_channel.send(' '.join(command[1:]))


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
