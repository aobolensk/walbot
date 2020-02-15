import asyncio
import datetime
import discord
import os
import random
import re
import requests
import urllib.request

from . import const
from . import emoji
from .config import Command
from .config import bc
from .config import BackgroundEvent
from .config import Reaction
from .config import log


class Commands:
    def __init__(self, config):
        self.config = config
        self.data = dict()

    def update_builtins(self):
        if not hasattr(self, "aliases"):
            self.aliases = dict()
        bc.commands = self
        if "len" not in self.data.keys():
            self.data["len"] = Command(
                "len", perform=self._len, permission=0,
                subcommand=True
            )
            self.data["len"].is_global = True
        if "count" not in self.data.keys():
            self.data["count"] = Command(
                "count", perform=self._count, permission=0,
                subcommand=True
            )
            self.data["count"].is_global = True
        if "ping" not in self.data.keys():
            self.data["ping"] = Command(
                "ping", perform=self._ping, permission=0,
                subcommand=False
            )
            self.data["ping"].is_global = True
        if "spoiler" not in self.data.keys():
            self.data["spoiler"] = Command(
                "spoiler", perform=self._spoiler, permission=0,
                subcommand=True
            )
            self.data["spoiler"].is_global = True
        if "help" not in self.data.keys():
            self.data["help"] = Command(
                "help", perform=self._help, permission=0,
                subcommand=False
            )
            self.data["help"].is_global = True
        if "profile" not in self.data.keys():
            self.data["profile"] = Command(
                "profile", perform=self._profile, permission=0,
                subcommand=False
            )
            self.data["profile"].is_global = True
        if "addcmd" not in self.data.keys():
            self.data["addcmd"] = Command(
                "addcmd", perform=self._addcmd, permission=1,
                subcommand=False
            )
            self.data["addcmd"].is_global = True
        if "updcmd" not in self.data.keys():
            self.data["updcmd"] = Command(
                "updcmd", perform=self._updcmd, permission=1,
                subcommand=False
            )
            self.data["updcmd"].is_global = True
        if "delcmd" not in self.data.keys():
            self.data["delcmd"] = Command(
                "delcmd", perform=self._delcmd, permission=1,
                subcommand=False
            )
            self.data["delcmd"].is_global = True
        if "enablecmd" not in self.data.keys():
            self.data["enablecmd"] = Command(
                "enablecmd", perform=self._enablecmd, permission=1,
                subcommand=False
            )
            self.data["enablecmd"].is_global = True
        if "disablecmd" not in self.data.keys():
            self.data["disablecmd"] = Command(
                "disablecmd", perform=self._disablecmd, permission=1,
                subcommand=False
            )
            self.data["disablecmd"].is_global = True
        if "permcmd" not in self.data.keys():
            self.data["permcmd"] = Command(
                "permcmd", perform=self._permcmd, permission=1,
                subcommand=False
            )
            self.data["permcmd"].is_global = True
        if "timescmd" not in self.data.keys():
            self.data["timescmd"] = Command(
                "timescmd", perform=self._timescmd, permission=0,
                subcommand=False
            )
            self.data["timescmd"].is_global = True
        if "permuser" not in self.data.keys():
            self.data["permuser"] = Command(
                "permuser", perform=self._permuser, permission=1,
                subcommand=False
            )
            self.data["permuser"].is_global = True
        if "whitelist" not in self.data.keys():
            self.data["whitelist"] = Command(
                "whitelist", perform=self._whitelist, permission=1,
                subcommand=False
            )
            self.data["whitelist"].is_global = True
        if "addreaction" not in self.data.keys():
            self.data["addreaction"] = Command(
                "addreaction", perform=self._addreaction, permission=1,
                subcommand=False
            )
            self.data["addreaction"].is_global = True
        if "updreaction" not in self.data.keys():
            self.data["updreaction"] = Command(
                "updreaction", perform=self._updreaction, permission=1,
                subcommand=False
            )
            self.data["updreaction"].is_global = True
        if "delreaction" not in self.data.keys():
            self.data["delreaction"] = Command(
                "delreaction", perform=self._delreaction, permission=1,
                subcommand=False
            )
            self.data["delreaction"].is_global = True
        if "listreaction" not in self.data.keys():
            self.data["listreaction"] = Command(
                "listreaction", perform=self._listreaction, permission=0,
                subcommand=False
            )
            self.data["listreaction"].is_global = True
        if "wme" not in self.data.keys():
            self.data["wme"] = Command(
                "wme", perform=self._wme, permission=1,
                subcommand=False
            )
            self.data["wme"].is_global = True
        if "poll" not in self.data.keys():
            self.data["poll"] = Command(
                "poll", perform=self._poll, permission=0,
                subcommand=False
            )
            self.data["poll"].is_global = True
        if "version" not in self.data.keys():
            self.data["version"] = Command(
                "version", perform=self._version, permission=0,
                subcommand=True
            )
            self.data["version"].is_global = True
        if "about" not in self.data.keys():
            self.data["about"] = Command(
                "about", perform=self._about, permission=0,
                subcommand=False
            )
            self.data["about"].is_global = True
        if "addbgevent" not in self.data.keys():
            self.data["addbgevent"] = Command(
                "addbgevent", perform=self._addbgevent, permission=1,
                subcommand=False
            )
            self.data["addbgevent"].is_global = True
        if "listbgevent" not in self.data.keys():
            self.data["listbgevent"] = Command(
                "listbgevent", perform=self._listbgevent, permission=0,
                subcommand=False
            )
            self.data["listbgevent"].is_global = True
        if "delbgevent" not in self.data.keys():
            self.data["delbgevent"] = Command(
                "delbgevent", perform=self._delbgevent, permission=1,
                subcommand=False
            )
            self.data["delbgevent"].is_global = True
        if "random" not in self.data.keys():
            self.data["random"] = Command(
                "random", perform=self._random, permission=0,
                subcommand=True
            )
            self.data["random"].is_global = True
        if "randselect" not in self.data.keys():
            self.data["randselect"] = Command(
                "randselect", perform=self._randselect, permission=0,
                subcommand=True
            )
            self.data["randselect"].is_global = True
        if "silent" not in self.data.keys():
            self.data["silent"] = Command(
                "silent", perform=self._silent, permission=0,
                subcommand=False
            )
            self.data["silent"].is_global = True
        if "time" not in self.data.keys():
            self.data["time"] = Command(
                "time", perform=self._time, permission=0,
                subcommand=True
            )
            self.data["time"].is_global = True
        if "uptime" not in self.data.keys():
            self.data["uptime"] = Command(
                "uptime", perform=self._uptime, permission=0,
                subcommand=True
            )
            self.data["uptime"].is_global = True
        if "status" not in self.data.keys():
            self.data["status"] = Command(
                "status", perform=self._status, permission=1,
                subcommand=False
            )
            self.data["status"].is_global = True
        if "forchannel" not in self.data.keys():
            self.data["forchannel"] = Command(
                "forchannel", perform=self._forchannel, permission=1,
                subcommand=False
            )
            self.data["forchannel"].is_global = True
        if "channelid" not in self.data.keys():
            self.data["channelid"] = Command(
                "channelid", perform=self._channelid, permission=1,
                subcommand=True
            )
            self.data["channelid"].is_global = True
        if "addalias" not in self.data.keys():
            self.data["addalias"] = Command(
                "addalias", perform=self._addalias, permission=1,
                subcommand=False
            )
            self.data["addalias"].is_global = True
        if "delalias" not in self.data.keys():
            self.data["delalias"] = Command(
                "delalias", perform=self._delalias, permission=1,
                subcommand=False
            )
            self.data["delalias"].is_global = True
        if "listalias" not in self.data.keys():
            self.data["listalias"] = Command(
                "listalias", perform=self._listalias, permission=0,
                subcommand=False
            )
            self.data["listalias"].is_global = True
        if "markov" not in self.data.keys():
            self.data["markov"] = Command(
                "markov", perform=self._markov, permission=0,
                subcommand=True
            )
            self.data["markov"].is_global = True
        if "markovgc" not in self.data.keys():
            self.data["markovgc"] = Command(
                "markovgc", perform=self._markovgc, permission=0,
                subcommand=False
            )
            self.data["markovgc"].is_global = True
        if "markovlog" not in self.data.keys():
            self.data["markovlog"] = Command(
                "markovlog", perform=self._markovlog, permission=1,
                subcommand=False
            )
            self.data["markovlog"].is_global = True
        if "delmarkov" not in self.data.keys():
            self.data["delmarkov"] = Command(
                "delmarkov", perform=self._delmarkov, permission=1,
                subcommand=False
            )
            self.data["delmarkov"].is_global = True
        if "findmarkov" not in self.data.keys():
            self.data["findmarkov"] = Command(
                "findmarkov", perform=self._findmarkov, permission=1,
                subcommand=False
            )
            self.data["findmarkov"].is_global = True
        if "dropmarkov" not in self.data.keys():
            self.data["dropmarkov"] = Command(
                "dropmarkov", perform=self._dropmarkov, permission=2,
                subcommand=False
            )
            self.data["dropmarkov"].is_global = True
        if "img" not in self.data.keys():
            self.data["img"] = Command(
                "img", perform=self._img, permission=0,
                subcommand=False
            )
            self.data["img"].is_global = True
        if "listimg" not in self.data.keys():
            self.data["listimg"] = Command(
                "listimg", perform=self._listimg, permission=0,
                subcommand=False
            )
            self.data["listimg"].is_global = True
        if "addimg" not in self.data.keys():
            self.data["addimg"] = Command(
                "addimg", perform=self._addimg, permission=1,
                subcommand=False
            )
            self.data["addimg"].is_global = True
        if "delimg" not in self.data.keys():
            self.data["delimg"] = Command(
                "delimg", perform=self._delimg, permission=1,
                subcommand=False
            )
            self.data["delimg"].is_global = True
        if "reactionwl" not in self.data.keys():
            self.data["reactionwl"] = Command(
                "reactionwl", perform=self._reactionwl, permission=1,
                subcommand=False
            )
            self.data["reactionwl"].is_global = True
        if "tts" not in self.data.keys():
            self.data["tts"] = Command(
                "tts", perform=self._tts, permission=1,
                subcommand=False
            )
            self.data["tts"].is_global = True
        if "urlencode" not in self.data.keys():
            self.data["urlencode"] = Command(
                "urlencode", perform=self._urlencode, permission=0,
                subcommand=True
            )
            self.data["urlencode"].is_global = True
        if "emojify" not in self.data.keys():
            self.data["emojify"] = Command(
                "emojify", perform=self._emojify, permission=0,
                subcommand=True
            )
            self.data["emojify"].is_global = True
        if "demojify" not in self.data.keys():
            self.data["demojify"] = Command(
                "demojify", perform=self._demojify, permission=0,
                subcommand=True
            )
            self.data["demojify"].is_global = True
        if "shutdown" not in self.data.keys():
            self.data["shutdown"] = Command(
                "shutdown", perform=self._shutdown, permission=2,
                subcommand=False
            )
            self.data["shutdown"].is_global = True
        if "avatar" not in self.data.keys():
            self.data["avatar"] = Command(
                "avatar", perform=self._avatar, permission=1,
                subcommand=False
            )
            self.data["avatar"].is_global = True
        if "echo" not in self.data.keys():
            self.data["echo"] = Command(
                "echo", message="@args@", permission=0,
                subcommand=False
            )
            self.data["echo"].is_global = True
        self.export_help()

    def export_help(self):
        with open(os.path.join(os.getcwd(), "docs", "Help.md"), "w", encoding="utf-8", newline='\n') as f:
            result = []
            for command in self.data:
                command = self.data[command]
                if command.perform is not None:
                    s = "**" + command.name + "**: "
                    s += " \\\n".join(command.perform.__doc__.split('\n'))
                    if command.subcommand:
                        s += " \\\n    *This command can be used as subcommand*"
                    s += '\n'
                    s = s.replace('<', '&lt;').replace('>', '&gt;')
                    result.append(s)
            result = list(set(result))
            result.sort()
            f.write('\n'.join(result))

    async def response(self, message, content, silent, **kwargs):
        if not silent:
            if content:
                for chunk in Command.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    await message.channel.send(chunk, tts=kwargs.get("tts", False))
            if kwargs.get("embed", None):
                await message.channel.send(embed=kwargs["embed"], tts=kwargs.get("tts", False))
        else:
            log.info("[SILENT] -> " + content)

    async def _len(self, message, command, silent=False):
        """Calculate length of the message
    Example: !len some text"""
        result = str(len(' '.join(command[1:])))
        await self.response(message, result, silent)
        return result

    async def _count(self, message, command, silent=False):
        """Count amount of words
    Example: !count some text"""
        result = str(len(command) - 1)
        await self.response(message, result, silent)
        return result

    async def _ping(self, message, command, silent=False):
        """Check whether the bot is active
    Example: !ping"""
        await self.response(message, "Pong! " + message.author.mention, silent)

    async def _spoiler(self, message, command, silent=False):
        """Mark text as spoiler
    Example: !spoiler hello"""
        result = "||" + ' '.join(command[1:]) + "||"
        await self.response(message, result, silent)
        return result

    async def _profile(self, message, command, silent=False):
        """Print information about user
    Examples:
        !profile
        !profile `@user`"""
        if len(command) == 1:
            info = message.author
        elif len(command) == 2:
            info = message.guild.get_member(message.mentions[0].id)
        else:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = message.author.mention + '\n'
        result += "User: " + str(info) + '\n'
        result += "Avatar: <" + str(info.avatar_url) + '>\n'
        status = [platform for (platform, status) in zip(
            ["desktop", "mobile", "browser"],
            [str(info.desktop_status), str(info.mobile_status), str(info.web_status)])
            if status != "offline"]
        result += "Status: " + str(info.status) + ' (' + ', '.join(status) + ')\n'
        result += "Created at: " + str(info.created_at) + '\n'
        await self.response(message, result, silent)

    async def _help(self, message, command, silent=False):
        """Print list of commands and get examples
    Examples:
        !help
        !help help"""
        if len(command) == 1:
            commands = []
            for command in self.data:
                command = self.data[command]
                if command.perform is None:
                    s = (command.name, command.message)
                    commands.append(s)
            commands.sort()
            version = self.config.get_version()
            if ' ' in version:
                version = "master"
            embed = discord.Embed(title="Help", color=0x717171)
            embed.add_field(
                name="Built-in commands",
                value=("<https://github.com/aobolensk/walbot/blob/" +
                       version + "/docs/Help.md>"),
                inline=False
            )
            for command in commands:
                embed.add_field(name=command[0], value=command[1], inline=False)
            await self.response(message, None, silent, embed=embed)
        elif len(command) == 2:
            if command[1] in self.data:
                command = self.data[command[1]]
            else:
                await self.response(message, "Unknown command '{}'".format(command[1]), silent)
                return
            result = command.name + ": "
            if command.perform is not None:
                result += command.perform.__doc__
            else:
                result += command.message
            result += '\n'
            result += "    Required permission level: {}\n".format(command.permission)
            if command.subcommand:
                result += "    This command can be used as subcommand\n"
            await self.response(message, result, silent)
        else:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)

    async def _addcmd(self, message, command, silent=False):
        """Add command
    Example: !addcmd hello Hello!"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        if command_name in self.data.keys():
            await self.response(message, "Command {} already exists".format(command_name), silent)
            return
        self.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        self.data[command_name].channels.append(message.channel.id)
        await self.response(message, "Command '{}' -> '{}' successfully added".format(
            command_name, self.data[command_name].message), silent)

    async def _updcmd(self, message, command, silent=False):
        """Update command (works only for commands that already exist)
    Example: !updcmd hello Hello!"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if self.data[command_name].message is None:
                await self.response(message, "Command '{}' is not editable".format(command_name), silent)
                return
            self.data[command_name].message = ' '.join(command[2:])
            await self.response(message, "Command '{}' -> '{}' successfully updated".format(
                command_name, self.data[command_name].message), silent)
            return
        await self.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _delcmd(self, message, command, silent=False):
        """Delete command
    Example: !delcmd hello"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        if command_name in self.data.keys():
            self.data.pop(command_name, None)
            await self.response(message, "Command '{}' successfully deleted".format(command_name), silent)
            return
        await self.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _enablecmd(self, message, command, silent=False):
        """Enable command in specified scope
    Examples:
        !enablecmd ping channel
        !enablecmd ping guild
        !enablecmd ping global"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                if message.channel.id not in self.data[command_name].channels:
                    self.data[command_name].channels.append(message.channel.id)
                await self.response(message, "Command '{}' is enabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id not in self.data[command_name].channels:
                        self.data[command_name].channels.append(channel.id)
                await self.response(message, "Command '{}' is enabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                self.data[command_name].is_global = True
                await self.response(message, "Command '{}' is enabled in global scope".format(command_name), silent)
            else:
                await self.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await self.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _disablecmd(self, message, command, silent=False):
        """Disable command in specified scope
    Examples:
        !disablecmd ping channel
        !disablecmd ping guild
        !disablecmd ping global"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                if message.channel.id in self.data[command_name].channels:
                    self.data[command_name].channels.remove(message.channel.id)
                await self.response(message, "Command '{}' is disabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in self.data[command_name].channels:
                        self.data[command_name].channels.remove(channel.id)
                await self.response(message, "Command '{}' is disabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                self.data[command_name].is_global = False
                await self.response(message, "Command '{}' is disabled in global scope".format(command_name), silent)
            else:
                await self.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await self.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _permcmd(self, message, command, silent=False):
        """Set commands permission
    Example: !permcmd ping 0"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        command_name = command[1]
        try:
            perm = int(command[2])
        except ValueError:
            await self.response(message, "Second argument of command '{}' should be an integer".format(
                command[0]), silent)
        if command_name in self.data.keys():
            self.data[command_name].permission = perm
            await self.response(message, "Set permission level {} for command '{}'".format(
                command[2], command_name), silent)
            return
        await self.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _timescmd(self, message, command, silent=False):
        """Print how many times command was invoked
    Example: !timescmd echo"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if command[1] not in self.data.keys():
            await self.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        com = self.data[command[1]]
        await self.response(message, "Command '{}' was invoked {} times".format(
            command[1],
            str(com.times_called if hasattr(com, "times_called") else 0)), silent)

    async def _permuser(self, message, command, silent=False):
        """Set user permission
    Example: !permcmd @nickname 0"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        try:
            perm = int(command[2])
        except ValueError:
            await self.response(message, "Second argument of command '{}' should be an integer".format(
                command[0]), silent)
        user_id = int(command[1][2:-1])
        for user in self.config.users.keys():
            if self.config.users[user].id == user_id:
                self.config.users[user].permission_level = perm
                await self.response(message, "User permissions are set to {}".format(command[2]), silent)
                return
        await self.response(message, "User '{}' is not found".format(command[1]), silent)

    async def _whitelist(self, message, command, silent=False):
        """Bot's whitelist
    Examples:
        !whitelist enable/disable
        !whitelist add
        !whitelist remove"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        if command[1] == "enable":
            self.config.guilds[message.channel.guild.id].is_whitelisted = True
            await self.response(message, "This guild is whitelisted for bot", silent)
        elif command[1] == "disable":
            self.config.guilds[message.channel.guild.id].is_whitelisted = False
            await self.response(message, "This guild is not whitelisted for bot", silent)
        elif command[1] == "add":
            self.config.guilds[message.channel.guild.id].whitelist.add(message.channel.id)
            await self.response(message, "This channel is added to bot's whitelist", silent)
        elif command[1] == "remove":
            self.config.guilds[message.channel.guild.id].whitelist.discard(message.channel.id)
            await self.response(message, "This channel is removed from bot's whitelist", silent)
        else:
            await self.response(message, "Unknown argument '{}'".format(command[1]), silent)

    async def _addreaction(self, message, command, silent=False):
        """Add reaction
    Example: !addreaction emoji regex"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        self.config.reactions.append(Reaction(' '.join(command[2:]), command[1]))
        await self.response(message, "Reaction '{}' on '{}' successfully added".format(
            command[1], ' '.join(command[2:])), silent)

    async def _updreaction(self, message, command, silent=False):
        """Update reaction
    Example: !updreaction index emoji regex"""
        if len(command) < 4:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        try:
            index = int(command[1])
        except Exception:
            await self.response(message, "Second parameter for '{}' should an index (integer)".format(
                command[0]), silent)
        if not (index >= 0 and index < len(self.config.reactions)):
            await self.response(message, "Incorrect index of reaction!", silent)
            return
        self.config.reactions[index] = Reaction(' '.join(command[3:]), command[2])
        await self.response(message, "Reaction '{}' on '{}' successfully updated".format(
            command[1], ' '.join(command[2:])), silent)

    async def _delreaction(self, message, command, silent=False):
        """Delete reaction
    Examples:
        !delreaction emoji
        !delreaction index"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        index = -1
        try:
            index = int(command[1])
            if not (index >= 0 and index < len(self.config.reactions)):
                await self.response(message, "Incorrect index of reaction!", silent)
                return
            reaction = self.config.reactions[index]
            self.config.reactions.pop(index)
            await self.response(message, "Reaction '{}' -> '{}' successfully removed".format(
                reaction.regex, reaction.emoji), silent)
        except Exception:
            i = 0
            while i < len(self.config.reactions):
                if self.config.reactions[i].emoji == command[1]:
                    self.config.reactions.pop(i)
                else:
                    i += 1
            await self.response(message, "Reaction '{}' successfully removed".format(command[1]), silent)

    async def _listreaction(self, message, command, silent=False):
        """Show list of reactions
    Example: !listreaction"""
        result = ""
        for reaction in self.config.reactions:
            result += reaction.emoji + ": " + reaction.regex + '\n'
        if len(result) > 0:
            await self.response(message, result, silent)
        else:
            await self.response(message, "No reactions found!", silent)

    async def _wme(self, message, command, silent=False):
        """Send direct message to author with something
    Example: !wme Hello!"""
        if message.author.dm_channel is None:
            await message.author.create_dm()
        result = ' '.join(command[1:])
        if len(result) == 0:
            return
        result = "You asked me to send you this: " + result
        if len(result) > const.DISCORD_MAX_MESSAGE_LENGTH:
            await message.author.dm_channel.send("<The message is too long>")
        else:
            await message.author.dm_channel.send(result)

    async def _poll(self, message, command, silent=False):
        """Create poll
    Example: !poll 60 option 1;option 2;option 3"""
        if silent:
            return
        try:
            duration = int(command[1])
        except ValueError:
            await message.channel.send("Second parameter for '{}' should be duration in seconds".format(command[0]))
            return
        options = ' '.join(command[2:])
        options = options.split(';')
        MAX_POLL_OPTIONS = 20
        if len(options) > MAX_POLL_OPTIONS:
            await message.channel.send("Too many options for poll")
            return
        poll_message = "Poll is started! You have " + command[1] + " seconds to vote!\n"
        for i in range(len(options)):
            poll_message += emoji.alphabet[i] + " -> " + options[i] + '\n'
        poll_message = await message.channel.send(poll_message)
        for i in range(len(options)):
            try:
                await poll_message.add_reaction(emoji.alphabet[i])
            except Exception:
                pass
        timestamps = [60]
        timestamps = [x for x in timestamps if x < duration]
        timestamps.append(duration)
        timestamps = (
            [timestamps[0]] + [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))])
        timestamps.reverse()
        remaining = duration
        for timestamp in timestamps:
            await asyncio.sleep(timestamp)
            remaining -= timestamp
            if remaining > 0:
                await message.channel.send("Poll is still going! {} seconds left".format(remaining))
            else:
                poll_message = poll_message.id
                poll_message = await message.channel.fetch_message(poll_message)
                results = []
                possible_answers = emoji.alphabet[:len(options)]
                for index, reaction in enumerate(poll_message.reactions):
                    if str(reaction) in possible_answers:
                        results.append((reaction, options[index], reaction.count - 1))
                results.sort(key=lambda option: option[2], reverse=True)
                result_message = "Time is up! Results:\n"
                for result in results:
                    result_message += str(result[0]) + " -> " + result[1] + " -> votes: " + str(result[2]) + '\n'
                await message.channel.send(result_message)
                for i in range(len(options)):
                    try:
                        await poll_message.remove_reaction(emoji.alphabet[i], poll_message.author)
                    except Exception:
                        pass
                return

    async def _version(self, message, command, silent=False):
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = self.config.get_version()
        if len(command) == 2 and (command[1] == 's' or command[1] == 'short'):
            result = result[:7]
        await self.response(message, result, silent)
        return result

    async def _about(self, message, command, silent=False):
        """Get information about the bot
    Example: !about"""
        result = "Source code: <https://github.com/aobolensk/walbot>"
        await self.response(message, result, silent)

    async def _addbgevent(self, message, command, silent=False):
        """Add background event
    Example: !addbgevent 60 ping"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        try:
            duration = int(command[1])
        except ValueError:
            await self.response(message, "Second parameter for '{}' should be duration in seconds".format(
                command[0]), silent)
            return
        message.content = self.config.commands_prefix + ' '.join(command[2:])
        bc.background_events.append(BackgroundEvent(
            self.config, message.channel, message, duration))
        await self.response(message, "Successfully added background event '{}' with period {}".format(
            message.content, str(duration)
        ), silent)

    async def _listbgevent(self, message, command, silent=False):
        """Print a list of background events
    Example: !listbgevent"""
        result = ""
        for index, event in enumerate(bc.background_events):
            result += "{}: '{}' every {} seconds\n".format(
                str(index), event.message.content, str(event.period)
            )
        if len(result) > 0:
            await self.response(message, result, silent)
        else:
            await self.response(message, "No background events found!", silent)

    async def _delbgevent(self, message, command, silent=False):
        """Delete background event
    Example: !delbgevent 0"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        try:
            index = int(command[1])
        except ValueError:
            await self.response(message, "Second parameter for '{}' should be an index of background event".format(
                command[0]), silent)
            return
        if index >= 0 and index < len(bc.background_events):
            bc.background_events[index].cancel()
            del bc.background_events[index]
        await self.response(message, "Successfully deleted background task!", silent)

    async def _random(self, message, command, silent=False):
        """Get random number in range [left, right]
    Example: !random 5 10"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        try:
            left = int(command[1])
            right = int(command[2])
        except ValueError:
            await self.response(message, "Range should be an integer!", silent)
            return
        if left > right:
            await self.response(message, "Left border should be less or equal than right", silent)
            return
        result = str(random.randint(left, right))
        await self.response(message, result, silent)
        return result

    async def _randselect(self, message, command, silent=False):
        """Get random option among provided strings
    Example: !randselect a b c"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        index = random.randint(1, len(command) - 1)
        result = command[index]
        await self.response(message, result, silent)
        return result

    async def _silent(self, message, command, silent=False):
        """Make the following command silent (without any output to the chat)
    Example: !silent ping"""
        if len(command) == 1:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        command = command[1:]
        if command[0] not in self.data.keys():
            await self.response(message, "Unknown command '{}'".format(command[0]), silent)
        else:
            actor = self.data[command[0]]
            await actor.run(message, command, None, silent=True)

    async def _time(self, message, command, silent=False):
        """Show current time and bot deployment time
    Example: !time"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = str(datetime.datetime.now()).split('.')[0]
        await self.response(message, result, silent)
        return result

    async def _uptime(self, message, command, silent=False):
        """Show bot uptime
    Example: !uptime"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        result = "{}:{:02}:{:02}:{:02}".format(days, hours, minutes, seconds)
        await self.response(message, result, silent)
        return result

    async def _status(self, message, command, silent=False):
        """Change bot status
    Examples:
        !status idle
        !status playing Dota 2
    Possible activities: [playing, streaming, watching, listening]
    Possible bot statuses: [online, idle, dnd, invisible]"""
        if len(command) == 1:
            await bc.change_status("", discord.ActivityType.playing)
        elif command[1] == "playing":
            await bc.change_status(' '.join(command[2:]), discord.ActivityType.playing)
        elif command[1] == "streaming":
            await bc.change_status(' '.join(command[2:]), discord.ActivityType.streaming)
        elif command[1] == "watching":
            await bc.change_status(' '.join(command[2:]), discord.ActivityType.watching)
        elif command[1] == "listening":
            await bc.change_status(' '.join(command[2:]), discord.ActivityType.listening)
        elif command[1] == "online":
            await bc.change_presence(status=discord.Status.online)
        elif command[1] == "idle":
            await bc.change_presence(status=discord.Status.idle)
        elif command[1] == "dnd":
            await bc.change_presence(status=discord.Status.dnd)
        elif command[1] == "invisible":
            await bc.change_presence(status=discord.Status.invisible)
        else:
            await self.response(message, "Unknown type of activity", silent)

    async def _forchannel(self, message, command, silent=False):
        """Executes command for channel
    Example: !forchannel <channel_id> ping"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        try:
            channel_id = int(command[1])
        except ValueError:
            await self.response(message, "Second argument of command '{}' should be an integer".format(
                command[0]), silent)
        message.channel = bc.get_channel(channel_id)
        command = command[2:]
        if command[0] not in self.data.keys():
            await self.response(message, "Unknown command '{}'".format(command[0]), silent)
        else:
            actor = self.data[command[0]]
            await actor.run(message, command, None, silent)

    async def _channelid(self, message, command, silent=False):
        """Get channel ID
    Example: !channelid"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = str(message.channel.id)
        await self.response(message, result, silent)
        return result

    async def _addalias(self, message, command, silent=False):
        """Add alias for commands
    Usage: !addalias <command> <alias>
    Example: !addalias ping pong"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        if command[1] not in self.data.keys():
            await self.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        if command[2] in self.data.keys():
            await self.response(message, "Command '{}' already exists".format(command[2]), silent)
            return
        if command[2] in self.aliases.keys():
            await self.response(message, "Alias '{}' already exists".format(command[2]), silent)
            return
        self.aliases[command[2]] = command[1]
        await self.response(message, "Alias '{}' for '{}' was successfully created".format(
            command[2], command[1]), silent)

    async def _delalias(self, message, command, silent=False):
        """Delete command alias
    Usage: !delalias <alias>
    Example: !delalias pong"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        if command[1] not in self.aliases.keys():
            await self.response(message, "Alias '{}' does not exist".format(command[1]), silent)
            return
        self.aliases.pop(command[1])
        await self.response(message, "Alias '{}' was successfully deleted".format(command[1]), silent)

    async def _listalias(self, message, command, silent=False):
        """Show list of aliases
    Example: !listalias"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = ""
        for alias, command in self.aliases.items():
            result += alias + " -> " + command + '\n'
        if len(result) > 0:
            await self.response(message, result, silent)

    async def _markov(self, message, command, silent=False):
        """Generate message using Markov chain
    Example: !markov"""
        result = ""
        if bc.bot_user.mentioned_in(message):
            result += message.author.mention + ' '
        result += bc.markov.generate()
        await self.response(message, result, silent)
        return result

    async def _markovgc(self, message, command, silent=False):
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        result = bc.markov.gc()
        result = f"Garbage collected {len(result)} items: {', '.join(result)}"
        await self.response(message, result, silent)
        return result

    async def _markovlog(self, message, command, silent=False):
        """Enable/disable adding messages from this channel to Markov model
    Examples:
        !markovlog
        !markovlog enable
        !markovlog disable"""
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) == 1:
            if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                await self.response(message, "Adding messages to model is enabled for this channel", silent)
            else:
                await self.response(message, "Adding messages to model is disabled for this channel", silent)
            return
        if command[1] == "enable":
            if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                await self.response(message, "Adding messages to model is already enabled for this channel", silent)
            else:
                self.config.guilds[message.channel.guild.id].markov_whitelist.add(message.channel.id)
                await self.response(
                    message, "Adding messages to model is successfully enabled for this channel", silent)
        elif command[1] == "disable":
            if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                self.config.guilds[message.channel.guild.id].markov_whitelist.discard(message.channel.id)
                await self.response(
                    message, "Adding messages to model is successfully disabled for this channel", silent)
            else:
                await self.response(message, "Adding messages to model is already disabled for this channel", silent)
        else:
            await self.response(message, "Unknown argument '{}'".format(command[1]), silent)

    async def _delmarkov(self, message, command, silent=False):
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        regex = ' '.join(command[1:])
        removed = bc.markov.del_words(regex)
        await self.response(message, "Deleted {} words from model: {}".format(str(len(removed)), str(removed)), silent)

    async def _findmarkov(self, message, command, silent=False):
        """Match words in Markov model using regex
    Example: !findmarkov hello"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        regex = ' '.join(command[1:])
        found = bc.markov.find_words(regex)
        await self.response(message, "Found {} words in model: {}".format(str(len(found)), str(found)), silent)

    async def _dropmarkov(self, message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        bc.markov.__init__()
        await self.response(message, "Markov database has been dropped!", silent)

    async def _img(self, message, command, silent=False):
        """Send image (use !listimg for list of available images)
    Example: !img"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if not silent and os.path.splitext(os.path.basename(file))[0].lower() == command[1].lower():
                        await message.channel.send(file=discord.File(os.path.join("images", file)))
                        return
        await self.response(message, "Image {} is not found!".format(command[1]), silent)

    async def _listimg(self, message, command, silent=False):
        """List of available images for !img command
    Example: !listimg"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        result = []
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    result.append(os.path.splitext(os.path.basename(file))[0])
        result.sort()
        if len(result) > 0:
            await self.response(message, "List of available images: [" + ', '.join(result) + "]", silent)
        else:
            await self.response(message, "No available images found!", silent)

    async def _addimg(self, message, command, silent=False):
        """Add image for !img command
    Example: !addimg name url"""
        if len(command) < 3:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 3:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            await self.response(message, "Incorrect name '{}'".format(name), silent)
            return
        url = command[2]
        ext = url.split('.')[-1]
        if ext not in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
            await self.response(message, "Please, provide direct link to image", silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if name == os.path.splitext(os.path.basename(file))[0]:
                        await self.response(message, "Image '{}' already exists".format(name), silent)
                        return
        if not os.path.exists("images"):
            os.makedirs("images")
        with open(os.path.join("images", name + '.' + ext), 'wb') as f:
            try:
                f.write(requests.get(url).content)
            except Exception:
                await self.response(message, "Image downloading failed!", silent)
                log.error("Image downloading failed!", exc_info=True)
                return
        await self.response(message, "Image '{}' successfully added!".format(name), silent)

    async def _delimg(self, message, command, silent=False):
        """Delete image for !img command
    Example: !delimg name"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            await self.response(message, "Incorrect name '{}'".format(name), silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if name == os.path.splitext(os.path.basename(file))[0]:
                        os.remove(os.path.join("images", file))
                        await self.response(message, "Successfully removed image '{}'".format(name), silent)
                        return
        await self.response(message, "Image '{}' not found!".format(name), silent)

    async def _reactionwl(self, message, command, silent=False):
        """Add/delete channel from reaction whitelist
    Examples:
        !reactionwl
        !reactionwl add
        !reactionwl delete"""
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) == 1:
            if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                await self.response(message, "Adding reactions is enabled for this channel", silent)
            else:
                await self.response(message, "Adding reactions is disabled for this channel", silent)
            return
        if command[1] == "add":
            if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                await self.response(message, "Adding reactions is already enabled for this channel", silent)
            else:
                self.config.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                await self.response(
                    message, "Adding reactions is successfully enabled for this channel", silent)
        elif command[1] == "delete":
            if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                self.config.guilds[message.channel.guild.id].reactions_whitelist.discard(message.channel.id)
                await self.response(
                    message, "Adding reactions is successfully disabled for this channel", silent)
            else:
                await self.response(message, "Adding reactions is already disabled for this channel", silent)
        else:
            await self.response(message, "Unknown argument '{}'".format(command[1]), silent)

    async def _tts(self, message, command, silent=False):
        """Send text-to-speech (TTS) message
    Example: !tts Hello!"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        text = ' '.join(command[1:])
        await self.response(message, text, silent, tts=True)
        log.debug("Sent TTS message: {}".format(text))

    async def _urlencode(self, message, command, silent=False):
        """Urlencode string
    Example: !urlencode hello, world!"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        result = ' '.join(command[1:])
        result = urllib.request.quote(result.encode("cp1251"))
        await self.response(message, result, silent)
        return result

    async def _emojify(self, message, command, silent=False):
        """Emojify text
    Example: !emojify Hello!"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        text = ' '.join(command[1:]).lower()
        result = ""
        is_emoji = False
        for i in range(len(text)):
            if not is_emoji:
                result += ' '
            if text[i] in emoji.text_to_emoji.keys():
                is_emoji = True
                result += emoji.text_to_emoji[text[i]] + ' '
            else:
                is_emoji = False
                result += text[i]
        result = result.strip()
        if len(result) > 0:
            await self.response(message, result, silent)
        return result

    async def _demojify(self, message, command, silent=False):
        """Demojify text
    Example: !demojify 🇭 🇪 🇱 🇱 🇴"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        text = ' '.join(command[1:]).lower()
        result = ""
        for i in range(len(text)):
            if text[i] in emoji.emoji_to_text.keys():
                result += emoji.emoji_to_text[text[i]]
            else:
                result += text[i]
        result = result.strip()
        if len(result) > 0:
            await self.response(message, result, silent)
        return result

    async def _shutdown(self, message, command, silent=False):
        """Shutdown the bot
    Example: !shutdown"""
        if len(command) > 1:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        log.info(str(message.author) + " invoked shutting down the bot")
        await bc.close()

    async def _avatar(self, message, command, silent=False):
        """Change bot avatar
    Example: !avatar <image>
    Hint: Use !listimg for list of available images"""
        if len(command) < 2:
            await self.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return
        if len(command) > 2:
            await self.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if os.path.splitext(os.path.basename(file))[0] == command[1]:
                        with open(os.path.join("images", file), "rb") as f:
                            await bc.bot_user.edit(avatar=f.read())
                        log.info("{} changed bot avatar to {}".format(
                            str(message.author),
                            command[1]))
                        return
        await self.response(message, "Image {} is not found!".format(command[1]), silent)
