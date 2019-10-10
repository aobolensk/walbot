import asyncio
import os

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

    async def run(self, message, command, user):
        if not self.is_available(message.channel.id):
            await message.channel.send("Command '{}' is not available in this channel".format(command[0]))
            return
        if self.permission > user.permission_level:
            await message.channel.send("You don't have permission to call command '{}'".format(command[0]))
            return
        if self.perform is not None:
            await self.perform(message, command)
        elif self.message is not None:
            respond = self.message
            respond = respond.replace("@author@", message.author.mention)
            respond = respond.replace("@args@", ' '.join(command[1:]))
            for i in range(len(command)):
                respond = respond.replace("@arg" + str(i) + "@", command[i])
            if (len(respond.strip()) > 0):
                await message.channel.send(respond)
        else:
            await message.channel.send("Command '{}' is not callable".format(command[0]))


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
        if "permcmd" not in self.data.keys():
            self.data["permcmd"] = Command("permcmd",
                perform=self._permcmd, permission=1)
            self.data["permcmd"].is_global = True
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
        if "poll" not in self.data.keys():
            self.data["poll"] = Command("poll",
                perform=self._poll, permission=0)
            self.data["poll"].is_global = True
        if "version" not in self.data.keys():
            self.data["version"] = Command("version",
                perform=self._version, permission=0)
            self.data["version"].is_global = True


    async def _ping(self, message, command):
        """Check whether the bot is active"""
        await message.channel.send("Pong! " + message.author.mention)

    async def _help(self, message, command):
        """Print list of commands and get examples
        Examples:
                !help
                !help help"""
        if len(command) == 1:
            result = []
            for command in self.data:
                command = self.data[command]
                s = command.name + ": "
                if command.perform is not None:
                    s += command.perform.__doc__.split('\n')[0]
                else:
                    s += command.message
                result.append(s)
            result.sort()
            await message.channel.send('\n'.join(result))
        elif len(command) == 2:
            if command[1] in self.data:
                command = self.data[command[1]]
            result = command.name + ": "
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

    async def _permcmd(self, message, command):
        """Set commands permission
        Example: !permcmd hello 0"""
        if len(command) < 3:
            await message.channel.send("Too few arguments for command 'permcmd'")
            return
        if len(command) > 3:
            await message.channel.send("Too many arguments for command 'permcmd'")
            return
        command_name = command[1]
        try:
            perm = int(command[2])
        except ValueError:
            await message.channel.send("Second argument of command 'permcmd' should be an integer")
        if command_name in self.data.keys():
            self.data[command_name].permission = perm
            await message.channel.send("Set permission level {} for command '{}'".format(command[2], command_name))
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
            await message.author.create_dm()
        if len(' '.join(command[1:])) > 0:
            await message.author.dm_channel.send(' '.join(command[1:]))

    async def _poll(self, message, command):
        """Create poll
        Example: !poll 60 option 1;option 2;option 3"""
        try:
            duration = int(command[1])
        except ValueError:
            await message.channel.send("Second parameter for 'poll' should be duration in seconds")
            return
        options = ' '.join(command[2:])
        options = options.split(';')
        alphabet = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"
        if len(options) > 26:
            await message.channel.send("Too many options for poll")
            return
        poll_message = "Poll is started! You have " + command[1] + " seconds to vote!\n"
        for i in range(len(options)):
            poll_message += alphabet[i] + " -> " + options[i] + '\n'
        poll_message = await message.channel.send(poll_message)
        for i in range(len(options)):
            await poll_message.add_reaction(alphabet[i])
        poll_message = poll_message.id
        await asyncio.sleep(duration)
        poll_message = await message.channel.fetch_message(poll_message)
        results = []
        for index, reaction in enumerate(poll_message.reactions):
            results.append((reaction, options[index], reaction.count - 1))
        results.sort(key=lambda option: option[2], reverse=True)
        result_message = "Time is up! Results:\n"
        for result in results:
            result_message += str(result[0]) + " -> " + result[1] + " -> votes: " + str(result[2]) + '\n'
        await message.channel.send(result_message)

    async def _version(self, message, command):
        """Get version of the bot"""
        if not os.path.exists(os.path.join(os.getcwd(), ".git")):
            await message.channel.send("Unable to get version (.git folder is not found)")
            return
        if not os.path.exists(os.path.join(os.getcwd(), ".git/HEAD")):
            await message.channel.send("Unable to get version (.git/HEAD file is not found)")
            return
        with open(os.path.join(os.getcwd(), ".git/HEAD")) as f:
            branch = f.readline()
            if branch[:5] != "ref: ":
                await message.channel.send("Unable to get version (.git/HEAD format is unknown)")
                return
            branch = branch[5:].strip()
        if not os.path.exists(os.path.join(os.getcwd(), ".git/" + branch)):
            await message.channel.send("Unable to get version (.git/" + branch + " file is not found)")
            return
        with open(os.path.join(os.getcwd(), ".git/" + branch)) as f:
            commit_hash = f.readline()
        await message.channel.send(commit_hash)
