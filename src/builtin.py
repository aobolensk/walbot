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
from .quote import Quote
from .reminder import Reminder
from .utils import Util


class BuiltinCommands:
    def __init__(self):
        self.config = bc.commands.config
        self.data = bc.commands.data

    def bind(self):
        if "takechars" not in self.data.keys():
            self.data["takechars"] = Command(
                "takechars", perform=self._takechars, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["takechars"].is_global = True
        if "countchars" not in self.data.keys():
            self.data["countchars"] = Command(
                "countchars", perform=self._countchars, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["countchars"].is_global = True
        if "takewords" not in self.data.keys():
            self.data["takewords"] = Command(
                "takewords", perform=self._takewords, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["takewords"].is_global = True
        if "countwords" not in self.data.keys():
            self.data["countwords"] = Command(
                "countwords", perform=self._countwords, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["countwords"].is_global = True
        if "takelines" not in self.data.keys():
            self.data["takelines"] = Command(
                "takelines", perform=self._takelines, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["takelines"].is_global = True
        if "countlines" not in self.data.keys():
            self.data["countlines"] = Command(
                "countlines", perform=self._countlines, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["countlines"].is_global = True
        if "tolower" not in self.data.keys():
            self.data["tolower"] = Command(
                "tolower", perform=self._tolower, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["tolower"].is_global = True
        if "toupper" not in self.data.keys():
            self.data["toupper"] = Command(
                "toupper", perform=self._toupper, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["toupper"].is_global = True
        if "ping" not in self.data.keys():
            self.data["ping"] = Command(
                "ping", perform=self._ping, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["ping"].is_global = True
        if "spoiler" not in self.data.keys():
            self.data["spoiler"] = Command(
                "spoiler", perform=self._spoiler, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["spoiler"].is_global = True
        if "help" not in self.data.keys():
            self.data["help"] = Command(
                "help", perform=self._help, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["help"].is_global = True
        if "profile" not in self.data.keys():
            self.data["profile"] = Command(
                "profile", perform=self._profile, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["profile"].is_global = True
        if "addcmd" not in self.data.keys():
            self.data["addcmd"] = Command(
                "addcmd", perform=self._addcmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addcmd"].is_global = True
        if "updcmd" not in self.data.keys():
            self.data["updcmd"] = Command(
                "updcmd", perform=self._updcmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["updcmd"].is_global = True
        if "delcmd" not in self.data.keys():
            self.data["delcmd"] = Command(
                "delcmd", perform=self._delcmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delcmd"].is_global = True
        if "enablecmd" not in self.data.keys():
            self.data["enablecmd"] = Command(
                "enablecmd", perform=self._enablecmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["enablecmd"].is_global = True
        if "disablecmd" not in self.data.keys():
            self.data["disablecmd"] = Command(
                "disablecmd", perform=self._disablecmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["disablecmd"].is_global = True
        if "permcmd" not in self.data.keys():
            self.data["permcmd"] = Command(
                "permcmd", perform=self._permcmd, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["permcmd"].is_global = True
        if "timescmd" not in self.data.keys():
            self.data["timescmd"] = Command(
                "timescmd", perform=self._timescmd, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["timescmd"].is_global = True
        if "permuser" not in self.data.keys():
            self.data["permuser"] = Command(
                "permuser", perform=self._permuser, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["permuser"].is_global = True
        if "whitelist" not in self.data.keys():
            self.data["whitelist"] = Command(
                "whitelist", perform=self._whitelist, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["whitelist"].is_global = True
        if "config" not in self.data.keys():
            self.data["config"] = Command(
                "config", perform=self._config, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["config"].is_global = True
        if "addreaction" not in self.data.keys():
            self.data["addreaction"] = Command(
                "addreaction", perform=self._addreaction, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addreaction"].is_global = True
        if "updreaction" not in self.data.keys():
            self.data["updreaction"] = Command(
                "updreaction", perform=self._updreaction, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["updreaction"].is_global = True
        if "delreaction" not in self.data.keys():
            self.data["delreaction"] = Command(
                "delreaction", perform=self._delreaction, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delreaction"].is_global = True
        if "listreaction" not in self.data.keys():
            self.data["listreaction"] = Command(
                "listreaction", perform=self._listreaction, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["listreaction"].is_global = True
        if "wme" not in self.data.keys():
            self.data["wme"] = Command(
                "wme", perform=self._wme, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["wme"].is_global = True
        if "poll" not in self.data.keys():
            self.data["poll"] = Command(
                "poll", perform=self._poll, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["poll"].is_global = True
        if "version" not in self.data.keys():
            self.data["version"] = Command(
                "version", perform=self._version, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["version"].is_global = True
        if "about" not in self.data.keys():
            self.data["about"] = Command(
                "about", perform=self._about, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["about"].is_global = True
        if "addbgevent" not in self.data.keys():
            self.data["addbgevent"] = Command(
                "addbgevent", perform=self._addbgevent, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addbgevent"].is_global = True
        if "listbgevent" not in self.data.keys():
            self.data["listbgevent"] = Command(
                "listbgevent", perform=self._listbgevent, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["listbgevent"].is_global = True
        if "delbgevent" not in self.data.keys():
            self.data["delbgevent"] = Command(
                "delbgevent", perform=self._delbgevent, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delbgevent"].is_global = True
        if "random" not in self.data.keys():
            self.data["random"] = Command(
                "random", perform=self._random, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["random"].is_global = True
        if "randselect" not in self.data.keys():
            self.data["randselect"] = Command(
                "randselect", perform=self._randselect, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["randselect"].is_global = True
        if "silent" not in self.data.keys():
            self.data["silent"] = Command(
                "silent", perform=self._silent, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["silent"].is_global = True
        if "time" not in self.data.keys():
            self.data["time"] = Command(
                "time", perform=self._time, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["time"].is_global = True
        if "uptime" not in self.data.keys():
            self.data["uptime"] = Command(
                "uptime", perform=self._uptime, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["uptime"].is_global = True
        if "status" not in self.data.keys():
            self.data["status"] = Command(
                "status", perform=self._status, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["status"].is_global = True
        if "forchannel" not in self.data.keys():
            self.data["forchannel"] = Command(
                "forchannel", perform=self._forchannel, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["forchannel"].is_global = True
        if "channelid" not in self.data.keys():
            self.data["channelid"] = Command(
                "channelid", perform=self._channelid, permission=const.Permission.MOD.value,
                subcommand=True)
            self.data["channelid"].is_global = True
        if "addalias" not in self.data.keys():
            self.data["addalias"] = Command(
                "addalias", perform=self._addalias, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addalias"].is_global = True
        if "delalias" not in self.data.keys():
            self.data["delalias"] = Command(
                "delalias", perform=self._delalias, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delalias"].is_global = True
        if "listalias" not in self.data.keys():
            self.data["listalias"] = Command(
                "listalias", perform=self._listalias, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["listalias"].is_global = True
        if "markov" not in self.data.keys():
            self.data["markov"] = Command(
                "markov", perform=self._markov, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["markov"].is_global = True
        if "markovgc" not in self.data.keys():
            self.data["markovgc"] = Command(
                "markovgc", perform=self._markovgc, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["markovgc"].is_global = True
        if "delmarkov" not in self.data.keys():
            self.data["delmarkov"] = Command(
                "delmarkov", perform=self._delmarkov, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delmarkov"].is_global = True
        if "findmarkov" not in self.data.keys():
            self.data["findmarkov"] = Command(
                "findmarkov", perform=self._findmarkov, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["findmarkov"].is_global = True
        if "dropmarkov" not in self.data.keys():
            self.data["dropmarkov"] = Command(
                "dropmarkov", perform=self._dropmarkov, permission=const.Permission.ADMIN.value,
                subcommand=False)
            self.data["dropmarkov"].is_global = True
        if "addmarkovfilter" not in self.data.keys():
            self.data["addmarkovfilter"] = Command(
                "addmarkovfilter", perform=self._addmarkovfilter, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addmarkovfilter"].is_global = True
        if "listmarkovfilter" not in self.data.keys():
            self.data["listmarkovfilter"] = Command(
                "listmarkovfilter", perform=self._listmarkovfilter, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["listmarkovfilter"].is_global = True
        if "delmarkovfilter" not in self.data.keys():
            self.data["delmarkovfilter"] = Command(
                "delmarkovfilter", perform=self._delmarkovfilter, permission=const.Permission.MOD.value,
                subcommand=True)
            self.data["delmarkovfilter"].is_global = True
        if "img" not in self.data.keys():
            self.data["img"] = Command(
                "img", perform=self._img, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["img"].is_global = True
        if "wmeimg" not in self.data.keys():
            self.data["wmeimg"] = Command(
                "wmeimg", perform=self._wmeimg, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["wmeimg"].is_global = True
        if "listimg" not in self.data.keys():
            self.data["listimg"] = Command(
                "listimg", perform=self._listimg, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["listimg"].is_global = True
        if "addimg" not in self.data.keys():
            self.data["addimg"] = Command(
                "addimg", perform=self._addimg, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["addimg"].is_global = True
        if "delimg" not in self.data.keys():
            self.data["delimg"] = Command(
                "delimg", perform=self._delimg, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["delimg"].is_global = True
        if "tts" not in self.data.keys():
            self.data["tts"] = Command(
                "tts", perform=self._tts, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["tts"].is_global = True
        if "urlencode" not in self.data.keys():
            self.data["urlencode"] = Command(
                "urlencode", perform=self._urlencode, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["urlencode"].is_global = True
        if "emojify" not in self.data.keys():
            self.data["emojify"] = Command(
                "emojify", perform=self._emojify, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["emojify"].is_global = True
        if "demojify" not in self.data.keys():
            self.data["demojify"] = Command(
                "demojify", perform=self._demojify, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["demojify"].is_global = True
        if "shutdown" not in self.data.keys():
            self.data["shutdown"] = Command(
                "shutdown", perform=self._shutdown, permission=const.Permission.ADMIN.value,
                subcommand=False)
            self.data["shutdown"].is_global = True
        if "avatar" not in self.data.keys():
            self.data["avatar"] = Command(
                "avatar", perform=self._avatar, permission=const.Permission.MOD.value,
                subcommand=False)
            self.data["avatar"].is_global = True
        if "message" not in self.data.keys():
            self.data["message"] = Command(
                "message", perform=self._message, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["message"].is_global = True
        if "reminder" not in self.data.keys():
            self.data["reminder"] = Command(
                "reminder", perform=self._reminder, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["reminder"].is_global = True
        if "listreminder" not in self.data.keys():
            self.data["listreminder"] = Command(
                "listreminder", perform=self._listreminder, permission=const.Permission.USER.value,
                subcommand=True)
            self.data["listreminder"].is_global = True
        if "delreminder" not in self.data.keys():
            self.data["delreminder"] = Command(
                "delreminder", perform=self._delreminder, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["delreminder"].is_global = True
        if "server" not in self.data.keys():
            self.data["server"] = Command(
                "server", perform=self._server, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["server"].is_global = True
        if "quote" not in self.data.keys():
            self.data["quote"] = Command(
                "quote", perform=self._quote, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["quote"].is_global = True
        if "addquote" not in self.data.keys():
            self.data["addquote"] = Command(
                "addquote", perform=self._addquote, permission=const.Permission.USER.value,
                subcommand=False)
            self.data["addquote"].is_global = True
        if "echo" not in self.data.keys():
            self.data["echo"] = Command(
                "echo", message="@args@", permission=const.Permission.USER.value,
                subcommand=False)
            self.data["echo"].is_global = True
        if "code" not in self.data.keys():
            self.data["code"] = Command(
                "code", message="`@args@`", permission=const.Permission.USER.value,
                subcommand=False)
            self.data["code"].is_global = True

    async def _takechars(self, message, command, silent=False):
        """Take n characters of the string
    Examples:
        !takechars 2 hello
        Result: he
        !takechars -2 hello
        Result: lo"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:])
        num = await Util.parse_int(message, command[1],
                                   "Second argument of command '{}' should be an integer".format(command[0]), silent)
        if num is None:
            return
        if num < 0:
            result = result[len(result)+num:]
        else:
            result = result[:num]
        await Util.response(message, result, silent)
        return result

    async def _countchars(self, message, command, silent=False):
        """Calculate length of the message
    Example: !countchars some text"""
        result = str(len(' '.join(command[1:])))
        await Util.response(message, result, silent)
        return result

    async def _takewords(self, message, command, silent=False):
        """Take n words of the string
    Examples:
        !takewords 2 a b c
        Result: a b
        !takewords -2 a b c
        Result: b c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split()
        num = await Util.parse_int(message, command[1],
                                   "Second argument of command '{}' should be an integer".format(command[0]), silent)
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[len(result)+num:])
        else:
            result = ' '.join(result[:num])
        await Util.response(message, result, silent)
        return result

    async def _countwords(self, message, command, silent=False):
        """Count amount of words
    Example: !count some text"""
        result = str(len(' '.join(command).split()) - 1)
        await Util.response(message, result, silent)
        return result

    async def _takelines(self, message, command, silent=False):
        """Take n lines of the string
    Examples:
        !takelines 2 a
        b
        c
        Result: a
        b
        !takelines -2 a
        b
        c
        Result: b
        c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split('\n')
        num = await Util.parse_int(message, command[1],
                                   "Second argument of command '{}' should be an integer".format(command[0]), silent)
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[len(result)+num:])
        else:
            result = '\n'.join(result[:num])
        await Util.response(message, result, silent)
        return result

    async def _countlines(self, message, command, silent=False):
        """Count amount of lines
    Example: !count some text"""
        result = str(len(' '.join(command).split('\n')))
        await Util.response(message, result, silent)
        return result

    async def _tolower(self, message, command, silent=False):
        """Convert text to lower case
    Example: !tolower SoMe TeXt"""
        result = ' '.join(command[1:]).lower()
        await Util.response(message, result, silent)
        return result

    async def _toupper(self, message, command, silent=False):
        """Convert text to upper case
    Example: !toupper SoMe TeXt"""
        result = ' '.join(command[1:]).upper()
        await Util.response(message, result, silent)
        return result

    async def _ping(self, message, command, silent=False):
        """Check whether the bot is active
    Example: !ping"""
        await Util.response(message, "Pong! " + message.author.mention, silent)

    async def _spoiler(self, message, command, silent=False):
        """Mark text as spoiler
    Example: !spoiler hello"""
        result = "||" + ' '.join(command[1:]) + "||"
        await Util.response(message, result, silent)
        return result

    async def _profile(self, message, command, silent=False):
        """Print information about user
    Examples:
        !profile
        !profile `@user`"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 1:
            info = message.author
        elif len(command) == 2:
            info = message.guild.get_member(message.mentions[0].id)
        result = message.author.mention + '\n'
        result += "User: " + str(info) + '\n'
        result += "Avatar: <" + str(info.avatar_url) + '>\n'
        status = [platform for (platform, status) in zip(
            ["desktop", "mobile", "browser"],
            [str(info.desktop_status), str(info.mobile_status), str(info.web_status)])
            if status != "offline"]
        result += "Status: " + str(info.status) + ' (' + ', '.join(status) + ')\n'
        result += "Created at: " + str(info.created_at) + '\n'
        result += "Roles: " + ', '.join(filter(lambda x: x != "@everyone", map(str, info.roles)))
        await Util.response(message, result, silent)

    async def _help(self, message, command, silent=False):
        """Print list of commands and get examples
    Examples:
        !help
        !help help"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
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
            await Util.response(message, None, silent, embed=embed)
        elif len(command) == 2:
            if command[1] in self.data:
                command = self.data[command[1]]
            elif command[1] in bc.commands.aliases.keys():
                command = self.data[bc.commands.aliases[command[1]]]
            else:
                await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
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
            await Util.response(message, result, silent)

    async def _addcmd(self, message, command, silent=False):
        """Add command
    Example: !addcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in self.data.keys():
            await Util.response(message, "Command {} already exists".format(command_name), silent)
            return
        self.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        self.data[command_name].channels.append(message.channel.id)
        await Util.response(message, "Command '{}' -> '{}' successfully added".format(
            command_name, self.data[command_name].message), silent)

    async def _updcmd(self, message, command, silent=False):
        """Update command (works only for commands that already exist)
    Example: !updcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if self.data[command_name].message is None:
                await Util.response(message, "Command '{}' is not editable".format(command_name), silent)
                return
            self.data[command_name].message = ' '.join(command[2:])
            await Util.response(message, "Command '{}' -> '{}' successfully updated".format(
                command_name, self.data[command_name].message), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _delcmd(self, message, command, silent=False):
        """Delete command
    Example: !delcmd hello"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        command_name = command[1]
        if command_name in self.data.keys():
            self.data.pop(command_name, None)
            await Util.response(message, "Command '{}' successfully deleted".format(command_name), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _enablecmd(self, message, command, silent=False):
        """Enable command in specified scope
    Examples:
        !enablecmd ping channel
        !enablecmd ping guild
        !enablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                if message.channel.id not in self.data[command_name].channels:
                    self.data[command_name].channels.append(message.channel.id)
                await Util.response(message, "Command '{}' is enabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id not in self.data[command_name].channels:
                        self.data[command_name].channels.append(channel.id)
                await Util.response(message, "Command '{}' is enabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                self.data[command_name].is_global = True
                await Util.response(message, "Command '{}' is enabled in global scope".format(command_name), silent)
            else:
                await Util.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _disablecmd(self, message, command, silent=False):
        """Disable command in specified scope
    Examples:
        !disablecmd ping channel
        !disablecmd ping guild
        !disablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        if command_name in self.data.keys():
            if command[2] == "channel":
                if message.channel.id in self.data[command_name].channels:
                    self.data[command_name].channels.remove(message.channel.id)
                await Util.response(message, "Command '{}' is disabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in self.data[command_name].channels:
                        self.data[command_name].channels.remove(channel.id)
                await Util.response(message, "Command '{}' is disabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                self.data[command_name].is_global = False
                await Util.response(message, "Command '{}' is disabled in global scope".format(command_name), silent)
            else:
                await Util.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _permcmd(self, message, command, silent=False):
        """Set commands permission
    Example: !permcmd ping 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        perm = await Util.parse_int(message, command[2],
                                    "Third argument of command '{}' should be an integer".format(command[0]), silent)
        if perm is None:
            return
        if command_name in self.data.keys():
            self.data[command_name].permission = perm
            await Util.response(message, "Set permission level {} for command '{}'".format(
                command[2], command_name), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    async def _timescmd(self, message, command, silent=False):
        """Print how many times command was invoked
    Example: !timescmd echo"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] not in self.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        com = self.data[command[1]]
        await Util.response(message, "Command '{}' was invoked {} times".format(
            command[1],
            str(com.times_called if hasattr(com, "times_called") else 0)), silent)

    async def _permuser(self, message, command, silent=False):
        """Set user permission
    Example: !permcmd @nickname 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        perm = await Util.parse_int(message, command[2],
                                    "Third argument of command '{}' should be an integer".format(command[0]), silent)
        if perm is None:
            return
        user_id = int(command[1][2:-1])
        for user in self.config.users.keys():
            if self.config.users[user].id == user_id:
                self.config.users[user].permission_level = perm
                await Util.response(message, "User permissions are set to {}".format(command[2]), silent)
                return
        await Util.response(message, "User '{}' is not found".format(command[1]), silent)

    async def _whitelist(self, message, command, silent=False):
        """Bot's whitelist
    Examples:
        !whitelist enable/disable
        !whitelist add
        !whitelist remove"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] == "enable":
            self.config.guilds[message.channel.guild.id].is_whitelisted = True
            await Util.response(message, "This guild is whitelisted for bot", silent)
        elif command[1] == "disable":
            self.config.guilds[message.channel.guild.id].is_whitelisted = False
            await Util.response(message, "This guild is not whitelisted for bot", silent)
        elif command[1] == "add":
            self.config.guilds[message.channel.guild.id].whitelist.add(message.channel.id)
            await Util.response(message, "This channel is added to bot's whitelist", silent)
        elif command[1] == "remove":
            self.config.guilds[message.channel.guild.id].whitelist.discard(message.channel.id)
            await Util.response(message, "This channel is removed from bot's whitelist", silent)
        else:
            await Util.response(message, "Unknown argument '{}'".format(command[1]), silent)

    async def _config(self, message, command, silent=False):
        """Setup some channel specific configurations
    Examples:
        !config reactions <enable/disable>
        !config markovlog <enable/disable>
        !config responses <enable/disable>
        !config markovpings <enable/disable>"""
        if not await Util.check_args_count(message, command, silent, min=1, max=3):
            return
        if len(command) == 1:
            result = "Config:\n"
            result += "Reactions: {}\n".format(
                "enabled" if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist
                else "disabled")
            result += "Markov logging: {}\n".format(
                "enabled" if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist
                else "disabled")
            result += "Markov responses: {}\n".format(
                "enabled" if message.channel.id in self.config.guilds[message.channel.guild.id].responses_whitelist
                else "disabled")
            result += "Markov pings: {}\n".format(
                "enabled" if self.config.guilds[message.channel.guild.id].markov_pings
                else "disabled")
            await Util.response(message, result, silent)
        elif len(command) == 3:
            if command[1] == "reactions":
                if command[2] == "enable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                        await Util.response(
                            message, "Adding reactions is already enabled for this channel", silent)
                    else:
                        self.config.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Adding reactions is successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
                        self.config.guilds[message.channel.guild.id].reactions_whitelist.discard(message.channel.id)
                        await Util.response(
                            message, "Adding reactions is successfully disabled for this channel", silent)
                    else:
                        await Util.response(
                            message, "Adding reactions is already disabled for this channel", silent)
                else:
                    await Util.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovlog":
                if command[2] == "enable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                        await Util.response(
                            message, "Adding messages to Markov model is already enabled for this channel", silent)
                    else:
                        self.config.guilds[message.channel.guild.id].markov_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Adding messages to Markov model is successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].markov_whitelist:
                        self.config.guilds[message.channel.guild.id].markov_whitelist.discard(message.channel.id)
                        await Util.response(
                            message, "Adding messages to Markov model is successfully disabled for this channel",
                            silent)
                    else:
                        await Util.response(
                            message, "Adding messages to Markov model is already disabled for this channel", silent)
            elif command[1] == "responses":
                if command[2] == "enable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].responses_whitelist:
                        await Util.response(
                            message, "Bot responses on mentioning are already enabled for this channel", silent)
                    else:
                        self.config.guilds[message.channel.guild.id].responses_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Bot responses on mentioning are successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in self.config.guilds[message.channel.guild.id].responses_whitelist:
                        self.config.guilds[message.channel.guild.id].responses_whitelist.discard(message.channel.id)
                        await Util.response(
                            message, "Bot responses on mentioning are successfully disabled for this channel",
                            silent)
                    else:
                        await Util.response(
                            message, "Bot responses on mentioning are already disabled for this channel", silent)
                else:
                    await Util.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovpings":
                if command[2] == "enable":
                    if self.config.guilds[message.channel.guild.id].markov_pings:
                        await Util.response(
                            message, "Markov pings are already enabled for this channel", silent)
                    else:
                        self.config.guilds[message.channel.guild.id].markov_pings = True
                        await Util.response(
                            message, "Markov pings are successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if self.config.guilds[message.channel.guild.id].markov_pings:
                        self.config.guilds[message.channel.guild.id].markov_pings = False
                        await Util.response(
                            message, "Markov pings are successfully disabled for this channel", silent)
                    else:
                        await Util.response(
                            message, "Markov pings are already disabled for this channel", silent)
                else:
                    await Util.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            else:
                await Util.response(message, "Incorrect argument for command '{}'".format(command[0]), silent)
        else:
            await Util.response(message, "Incorrect usage of command '{}'".format(command[0]), silent)

    async def _addreaction(self, message, command, silent=False):
        """Add reaction
    Example: !addreaction emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        self.config.reactions.append(Reaction(' '.join(command[2:]), command[1]))
        await Util.response(message, "Reaction '{}' on '{}' successfully added".format(
            command[1], ' '.join(command[2:])), silent)

    async def _updreaction(self, message, command, silent=False):
        """Update reaction
    Example: !updreaction index emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should an index (integer)".format(command[0]), silent)
        if index is None:
            return
        if not (index >= 0 and index < len(self.config.reactions)):
            await Util.response(message, "Incorrect index of reaction!", silent)
            return
        self.config.reactions[index] = Reaction(' '.join(command[3:]), command[2])
        await Util.response(message, "Reaction '{}' on '{}' successfully updated".format(
            command[1], ' '.join(command[2:])), silent)

    async def _delreaction(self, message, command, silent=False):
        """Delete reaction
    Examples:
        !delreaction emoji
        !delreaction index"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = -1
        try:
            index = int(command[1])
            if not (index >= 0 and index < len(self.config.reactions)):
                await Util.response(message, "Incorrect index of reaction!", silent)
                return
            reaction = self.config.reactions[index]
            self.config.reactions.pop(index)
            await Util.response(message, "Reaction '{}' -> '{}' successfully removed".format(
                reaction.regex, reaction.emoji), silent)
        except Exception:
            i = 0
            while i < len(self.config.reactions):
                if self.config.reactions[i].emoji == command[1]:
                    self.config.reactions.pop(i)
                else:
                    i += 1
            await Util.response(message, "Reaction '{}' successfully removed".format(command[1]), silent)

    async def _listreaction(self, message, command, silent=False):
        """Show list of reactions
    Example: !listreaction"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, reaction in enumerate(self.config.reactions):
            result += "{} - {}: {}\n".format(index, reaction.emoji, reaction.regex)
        if len(result) > 0:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reactions found!", silent)
        return result

    async def _wme(self, message, command, silent=False):
        """Send direct message to author with something
    Example: !wme Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[1:])
        if len(result) == 0:
            return
        result = "You asked me to send you this: " + result
        await Util.send_direct_message(message, result, silent)

    async def _poll(self, message, command, silent=False):
        """Create poll
    Example: !poll 60 option 1;option 2;option 3"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        if silent:
            return
        duration = await Util.parse_int(message, command[1],
                                        "Second parameter for '{}' should be duration in seconds".format(command[0]),
                                        silent)
        if duration is None:
            return
        options = ' '.join(command[2:])
        options = options.split(';')
        if len(options) > const.MAX_POLL_OPTIONS:
            await Util.response(message, "Too many options for poll", silent)
            return
        poll_message = "Poll is started! You have " + command[1] + " seconds to vote!\n"
        for i in range(len(options)):
            poll_message += emoji.alphabet[i] + " -> " + options[i] + '\n'
        poll_message = await message.channel.send(poll_message)
        for i in range(len(options)):
            try:
                await poll_message.add_reaction(emoji.alphabet[i])
            except Exception:
                log.debug("Error on add_reaction: {}".format(emoji.alphabet[i]))
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
                await Util.response(message, "Poll is still going! {} seconds left".format(remaining), silent)
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
                await Util.response(message, result_message, silent)
                for i in range(len(options)):
                    try:
                        await poll_message.remove_reaction(emoji.alphabet[i], poll_message.author)
                    except Exception:
                        log.debug("Error on remove_reaction: {}".format(emoji.alphabet[i]))
                return

    async def _version(self, message, command, silent=False):
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        result = self.config.get_version()
        if len(command) == 2 and (command[1] == 's' or command[1] == 'short'):
            result = result[:7]
        await Util.response(message, result, silent)
        return result

    async def _about(self, message, command, silent=False):
        """Get information about the bot
    Example: !about"""
        result = str(bc.bot_user) + ' (WalBot instance)\n'
        result += "Source code: <https://github.com/aobolensk/walbot>\n"
        result += "Version: " + self.config.get_version() + '\n'
        result += "Uptime: " + self.config.get_uptime() + '\n'
        await Util.response(message, result, silent)

    async def _addbgevent(self, message, command, silent=False):
        """Add background event
    Example: !addbgevent 60 ping"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        duration = await Util.parse_int(message, command[1],
                                        "Second parameter for '{}' should be duration in seconds".format(command[0]),
                                        silent)
        if duration is None:
            return
        message.content = self.config.commands_prefix + ' '.join(command[2:])
        bc.background_events.append(BackgroundEvent(
            self.config, message.channel, message, duration))
        await Util.response(message, "Successfully added background event '{}' with period {}".format(
            message.content, str(duration)
        ), silent)

    async def _listbgevent(self, message, command, silent=False):
        """Print a list of background events
    Example: !listbgevent"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, event in enumerate(bc.background_events):
            result += "{}: '{}' every {} seconds\n".format(
                str(index), event.message.content, str(event.period)
            )
        if len(result) > 0:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No background events found!", silent)
        return result

    async def _delbgevent(self, message, command, silent=False):
        """Delete background event
    Example: !delbgevent 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of background event"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if index >= 0 and index < len(bc.background_events):
            bc.background_events[index].cancel()
            del bc.background_events[index]
            await Util.response(message, "Successfully deleted background task!", silent)
        else:
            await Util.response(message, "Invalid index of background task!", silent)

    async def _random(self, message, command, silent=False):
        """Get random number in range [left, right]
    Example: !random 5 10"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        left = await Util.parse_int(message, command[1],
                                    "Left border should be an integer", silent)
        if left is None:
            return
        right = await Util.parse_int(message, command[2],
                                     "Right border should be an integer", silent)
        if right is None:
            return
        if left > right:
            await Util.response(message, "Left border should be less or equal than right", silent)
            return
        result = str(random.randint(left, right))
        await Util.response(message, result, silent)
        return result

    async def _randselect(self, message, command, silent=False):
        """Get random option among provided strings
    Example: !randselect a b c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        index = random.randint(1, len(command) - 1)
        result = command[index]
        await Util.response(message, result, silent)
        return result

    async def _silent(self, message, command, silent=False):
        """Make the following command silent (without any output to the chat)
    Example: !silent ping"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        command = command[1:]
        if command[0] not in self.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[0]), silent)
        else:
            actor = self.data[command[0]]
            await actor.run(message, command, None, silent=True)

    async def _time(self, message, command, silent=False):
        """Show current time
    Example: !time"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = str(datetime.datetime.now()).split('.')[0]
        await Util.response(message, result, silent)
        return result

    async def _uptime(self, message, command, silent=False):
        """Show bot uptime
    Example: !uptime"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = self.config.get_uptime()
        await Util.response(message, result, silent)
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
            await Util.response(message, "Unknown type of activity", silent)

    async def _forchannel(self, message, command, silent=False):
        """Executes command for channel
    Example: !forchannel <channel_id> ping"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        channel_id = await Util.parse_int(message, command[1],
                                          "Second argument of command '{}' should be an integer".format(command[0]),
                                          silent)
        if channel_id is None:
            return
        message.channel = bc.get_channel(channel_id)
        command = command[2:]
        message.content = ' '.join(command)
        if command[0] not in self.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[0]), silent)
        else:
            actor = self.data[command[0]]
            await actor.run(message, command, None, silent)

    async def _channelid(self, message, command, silent=False):
        """Get channel ID
    Example: !channelid"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = str(message.channel.id)
        await Util.response(message, result, silent)
        return result

    async def _addalias(self, message, command, silent=False):
        """Add alias for commands
    Usage: !addalias <command> <alias>
    Example: !addalias ping pong"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        if command[1] not in self.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        if command[2] in self.data.keys():
            await Util.response(message, "Command '{}' already exists".format(command[2]), silent)
            return
        if command[2] in bc.commands.aliases.keys():
            await Util.response(message, "Alias '{}' already exists".format(command[2]), silent)
            return
        bc.commands.aliases[command[2]] = command[1]
        await Util.response(message, "Alias '{}' for '{}' was successfully created".format(
            command[2], command[1]), silent)

    async def _delalias(self, message, command, silent=False):
        """Delete command alias
    Usage: !delalias <alias>
    Example: !delalias pong"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] not in bc.commands.aliases.keys():
            await Util.response(message, "Alias '{}' does not exist".format(command[1]), silent)
            return
        bc.commands.aliases.pop(command[1])
        await Util.response(message, "Alias '{}' was successfully deleted".format(command[1]), silent)

    async def _listalias(self, message, command, silent=False):
        """Show list of aliases
    Example: !listalias"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for alias, command in bc.commands.aliases.items():
            result += alias + " -> " + command + '\n'
        await Util.response(message, result, silent)
        return result

    async def _markov(self, message, command, silent=False):
        """Generate message using Markov chain
    Example: !markov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = await self.config.disable_pings_in_response(message, bc.markov.generate())
        await Util.response(message, result, silent)
        return result

    async def _markovgc(self, message, command, silent=False):
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.markov.gc()
        result = "Garbage collected {} items: {}".format(len(result), ', '.join(result))
        await Util.response(message, result, silent)
        return result

    async def _delmarkov(self, message, command, silent=False):
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        removed = bc.markov.del_words(regex)
        await Util.response(message, "Deleted {} words from model: {}".format(str(len(removed)),
                            str(removed)), silent, suppress_embeds=True)

    async def _findmarkov(self, message, command, silent=False):
        """Match words in Markov model using regex
    Example: !findmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        found = bc.markov.find_words(regex)
        await Util.response(message, "Found {} words in model: {}".format(str(len(found)),
                            str(found)), silent, suppress_embeds=True)

    async def _dropmarkov(self, message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        bc.markov.__init__()
        await Util.response(message, "Markov database has been dropped!", silent)

    async def _addmarkovfilter(self, message, command, silent=False):
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        bc.markov.filters.append(re.compile(command[1]))
        await Util.response(message, "Filter '{}' was successfully added for Markov model".format(command[1]), silent)

    async def _listmarkovfilter(self, message, command, silent=False):
        """Print a list of regular expression filters for Markov model
    Example: !listmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, regex in enumerate(bc.markov.filters):
            result += "{} -> {}\n".format(index, regex.pattern)
        if len(result) > 0:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No filters for Markov model found!", silent)
        return result

    async def _delmarkovfilter(self, message, command, silent=False):
        """Delete regular expression filter for Markov model by index
    Example: !delmarkovfilter 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of filter"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if index >= 0 and index < len(bc.markov.filters):
            bc.markov.filters.pop(index)
            await Util.response(message, "Successfully deleted filter!", silent)
        else:
            await Util.response(message, "Invalid index of filter!", silent)

    async def _img(self, message, command, silent=False):
        """Send image (use !listimg for list of available images)
    Example: !img <image_name>"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        for i in range(1, len(command)):
            for root, _, files in os.walk("images"):
                if root.endswith("images"):
                    for file in files:
                        if not silent and os.path.splitext(os.path.basename(file))[0].lower() == command[i].lower():
                            await Util.response(message, None, silent,
                                                files=[discord.File(os.path.join("images", file))])
                            break
                    else:
                        r = const.EMOJI_REGEX.match(command[i])
                        if r is not None:
                            await Util.response(message,
                                                "https://cdn.discordapp.com/emojis/{}.png".format(r.group(2)), silent)
                            break
                        await Util.response(message, "Image {} is not found!".format(command[1]), silent)
                    break

    async def _wmeimg(self, message, command, silent=False):
        """Send image in direct message to author
    Example: !wmeimg <image_name>"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        for i in range(1, len(command)):
            for root, _, files in os.walk("images"):
                if root.endswith("images"):
                    for file in files:
                        if not silent and os.path.splitext(os.path.basename(file))[0].lower() == command[i].lower():
                            await Util.send_direct_message(message, None, silent,
                                                           files=[discord.File(os.path.join("images", file))])
                            break
                    else:
                        r = const.EMOJI_REGEX.match(command[i])
                        if r is not None:
                            await Util.response(message,
                                                "https://cdn.discordapp.com/emojis/{}.png".format(r.group(2)), silent)
                            break
                    break

    async def _listimg(self, message, command, silent=False):
        """List of available images for !img command
    Example: !listimg"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = []
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    result.append(os.path.splitext(os.path.basename(file))[0])
        result.sort()
        if len(result) > 0:
            await Util.response(message, "List of available images: [" + ', '.join(result) + "]", silent)
        else:
            await Util.response(message, "No available images found!", silent)

    async def _addimg(self, message, command, silent=False):
        """Add image for !img command
    Example: !addimg name url"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            await Util.response(message, "Incorrect name '{}'".format(name), silent)
            return
        url = command[2]
        ext = url.split('.')[-1]
        if ext not in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
            await Util.response(message, "Please, provide direct link to image", silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if name == os.path.splitext(os.path.basename(file))[0]:
                        await Util.response(message, "Image '{}' already exists".format(name), silent)
                        return
        if not os.path.exists("images"):
            os.makedirs("images")
        with open(os.path.join("images", name + '.' + ext), 'wb') as f:
            try:
                f.write(requests.get(url).content)
            except Exception:
                await Util.response(message, "Image downloading failed!", silent)
                log.error("Image downloading failed!", exc_info=True)
                return
        await Util.response(message, "Image '{}' successfully added!".format(name), silent)

    async def _delimg(self, message, command, silent=False):
        """Delete image for !img command
    Example: !delimg name"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            await Util.response(message, "Incorrect name '{}'".format(name), silent)
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if name == os.path.splitext(os.path.basename(file))[0]:
                        os.remove(os.path.join("images", file))
                        await Util.response(message, "Successfully removed image '{}'".format(name), silent)
                        return
        await Util.response(message, "Image '{}' not found!".format(name), silent)

    async def _tts(self, message, command, silent=False):
        """Send text-to-speech (TTS) message
    Example: !tts Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        text = ' '.join(command[1:])
        await Util.response(message, text, silent, tts=True)
        log.debug("Sent TTS message: {}".format(text))

    async def _urlencode(self, message, command, silent=False):
        """Urlencode string
    Example: !urlencode hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[1:])
        result = urllib.request.quote(result.encode("cp1251"))
        await Util.response(message, result, silent)
        return result

    async def _emojify(self, message, command, silent=False):
        """Emojify text
    Example: !emojify Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
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
        await Util.response(message, result, silent)
        return result

    async def _demojify(self, message, command, silent=False):
        """Demojify text
    Example: !demojify 🇭 🇪 🇱 🇱 🇴"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        text = ''.join(command[1:]).lower()
        result = ""
        for i in range(len(text)):
            if text[i] in emoji.emoji_to_text.keys():
                result += emoji.emoji_to_text[text[i]]
            else:
                result += text[i]
        result = result.strip()
        await Util.response(message, result, silent)
        return result

    async def _shutdown(self, message, command, silent=False):
        """Shutdown the bot
    Example: !shutdown"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        log.info(str(message.author) + " invoked shutting down the bot")
        await bc.close()

    async def _avatar(self, message, command, silent=False):
        """Change bot avatar
    Example: !avatar <image>
    Hint: Use !listimg for list of available images"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
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
        await Util.response(message, "Image {} is not found!".format(command[1]), silent)

    async def _message(self, message, command, silent=False):
        """Get message by its order number (from the end of channel history)
    Example: !message"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        number = await Util.parse_int(message, command[1],
                                      "Message number should be an integer", silent)
        if number is None:
            return
        if number <= 0:
            await Util.response(message, "Invalid message number", silent)
            return
        if number > const.MAX_MESSAGE_HISTORY_DEPTH:
            await Util.response(message,
                                "Message search depth is too big (it can't be more than {})"
                                .format(const.MAX_MESSAGE_HISTORY_DEPTH), silent)
            return
        result = await message.channel.history(limit=number+1).flatten()
        result = result[-1].content
        await Util.response(message, result, silent)
        return result

    async def _reminder(self, message, command, silent=False):
        """Print message at particular time
    Example: !reminder 2020-01-01 00:00 Happy new year!"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        time = command[1] + ' ' + command[2]
        try:
            time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
        except ValueError:
            await Util.response(message, "{} does not match format {}\n"
                                "More information about format: <https://strftime.org/>".format(
                                    time, const.REMINDER_TIME_FORMAT),
                                silent)
            return
        text = ' '.join(command[3:])
        self.config.reminders.append(Reminder(str(time), text, message.channel.id))
        await Util.response(message, "Reminder '{}' added at {}".format(text, time), silent)

    async def _listreminder(self, message, command, silent=False):
        """Print list of reminders
    Example: !listreminder"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        result = ""
        reminders = sorted(zip(range(0, len(self.config.reminders)), self.config.reminders), key=lambda x: x[1])
        for index, reminder in reminders:
            result += "{} - {} (channel: {}) -> {}\n".format(
                index, reminder.time, reminder.channel_id, reminder.message)
        if len(result) > 0:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reminders found!", silent)
        return result

    async def _delreminder(self, message, command, silent=False):
        """Delete reminder by index
    Example: !delreminder 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of reminder"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if index >= 0 and index < len(self.config.reminders):
            self.config.reminders.pop(index)
            await Util.response(message, "Successfully deleted reminder!", silent)
        else:
            await Util.response(message, "Invalid index of reminder!", silent)

    async def _server(self, message, command, silent=False):
        """Print information about current server
    Example: !server 0"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        g = message.guild
        result = "**Server**: '{}', members: {}, region: {}, created: {}\n".format(
            g.name, g.member_count, g.region, g.created_at.replace(microsecond=0))
        result += "**Icon**: {}\n".format("<{}>".format(g.icon_url))
        if g.member_count <= 16:
            result += "**Members**:\n"
            members = []
            async for member in g.fetch_members(limit=16):
                members.append("*{} ({}):*\n{}".format(
                    str(member),
                    (("owner, " if member.id == g.owner_id else "") +
                     str(message.guild.get_member(member.id).status)),
                    ', '.join(filter(lambda x: x != "@everyone", map(str, member.roles)))))
            result += '\n'.join(sorted(members, key=lambda s: s.lower()))
        await Util.response(message, result, silent)

    async def _quote(self, message, command, silent=False):
        """Print some quote from quotes database
    Examples:
        !quote
        !quote 1"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(self.config.quotes) == 0:
            await Util.response(message, "<Quotes database is empty>", silent)
            return
        if len(command) == 2:
            index = await Util.parse_int(message, command[1],
                                         "Second parameter for '{}' should be an index of quote"
                                         .format(command[0]),
                                         silent)
            if index is None:
                return
        else:
            index = random.randint(0, len(self.config.quotes) - 1)
        if index >= 0 and index < len(self.config.quotes):
            await Util.response(message, "Quote {}: {}".format(index, self.config.quotes[index].full_quote()), silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)

    async def _addquote(self, message, command, silent=False):
        """Add quote to quotes database
    Example: !addquote Hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        quote = ' '.join(command[1:])
        self.config.quotes.append(Quote(quote, str(message.author)))
        await Util.response(message,
                            "Quote '{}' was successfully added to quotes database with index {}".format(
                                quote, len(self.config.quotes) - 1), silent)
