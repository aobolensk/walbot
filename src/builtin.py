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
from .config import BackgroundEvent
from .config import Command
from .config import Reaction
from .config import bc
from .config import log
from .quote import Quote
from .reminder import Reminder
from .utils import Util


class BuiltinCommands:
    def bind(self):
        bc.commands.register_command(__name__, self.__class__.__name__, "takechars",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "countchars",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "takewords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "countwords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "takelines",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "countlines",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "tolower",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "toupper",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "range",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "ping",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "spoiler",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "help",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "profile",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "updcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "enablecmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "disablecmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "permcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "timescmd",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "permuser",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "whitelist",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "config",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "updreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listreaction",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "wme",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "poll",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "version",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "about",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addbgevent",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listbgevent",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "delbgevent",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "random",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "randselect",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "silent",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "time",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "uptime",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "status",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "channelid",
                                     permission=const.Permission.MOD.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "addalias",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delalias",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listalias",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "markov",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "markovgc",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delmarkov",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "findmarkov",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "dropmarkov",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addmarkovfilter",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listmarkovfilter",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "delmarkovfilter",
                                     permission=const.Permission.MOD.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "img",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "wmeimg",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listimg",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addimg",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delimg",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "tts",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "urlencode",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "emojify",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "demojify",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "shutdown",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "avatar",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "message",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "reminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "updreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listreminder",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "delreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "server",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "quote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "addquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "listquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "delquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "setquoteauthor",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__class__.__name__, "echo",
                                     message="@args@",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__class__.__name__, "code",
                                     message="`@args@`",
                                     permission=const.Permission.USER.value, subcommand=True)

    @staticmethod
    async def _takechars(message, command, silent=False):
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

    @staticmethod
    async def _countchars(message, command, silent=False):
        """Calculate length of the message
    Example: !countchars some text"""
        result = str(len(' '.join(command[1:])))
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _takewords(message, command, silent=False):
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

    @staticmethod
    async def _countwords(message, command, silent=False):
        """Count amount of words
    Example: !count some text"""
        result = str(len(' '.join(command).split()) - 1)
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _takelines(message, command, silent=False):
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

    @staticmethod
    async def _countlines(message, command, silent=False):
        """Count amount of lines
    Example: !count some text"""
        result = str(len(' '.join(command).split('\n')))
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _tolower(message, command, silent=False):
        """Convert text to lower case
    Example: !tolower SoMe TeXt"""
        result = ' '.join(command[1:]).lower()
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _toupper(message, command, silent=False):
        """Convert text to upper case
    Example: !toupper SoMe TeXt"""
        result = ' '.join(command[1:]).upper()
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _range(message, command, silent=False):
        """Generate range of numbers
    Examples:
        !range <stop>
        !range <start> <stop>
        !range <start> <stop> <step>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=4):
            return
        start, stop, step = 0, 0, 1
        if len(command) == 2:
            stop = await Util.parse_int(message, command[1],
                                        "Stop parameter in range '{}' should be an integer".format(command[0]),
                                        silent)
        else:
            start = await Util.parse_int(message, command[1],
                                         "Start parameter in range '{}' should be an integer".format(command[0]),
                                         silent)
            stop = await Util.parse_int(message, command[2],
                                        "Stop parameter in range '{}' should be an integer".format(command[0]),
                                        silent)
            if len(command) == 4:
                step = await Util.parse_int(message, command[3],
                                            "Step parameter in range '{}' should be an integer".format(command[0]),
                                            silent)
        if start is None or stop is None or step is None:
            return
        result = ''
        for iteration, number in enumerate(range(start, stop, step)):
            if iteration >= const.MAX_RANGE_ITERATIONS:
                result = "Range iteration limit ({}) has exceeded".format(const.MAX_RANGE_ITERATIONS)
                break
            result += str(number) + ' '
        else:
            result = result[:-1]
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _ping(message, command, silent=False):
        """Check whether the bot is active
    Example: !ping"""
        await Util.response(message, "Pong! " + message.author.mention, silent)

    @staticmethod
    async def _spoiler(message, command, silent=False):
        """Mark text as spoiler
    Example: !spoiler hello"""
        result = "||" + ' '.join(command[1:]) + "||"
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _profile(message, command, silent=False):
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

    @staticmethod
    async def _help(message, command, silent=False):
        """Print list of commands and get examples
    Examples:
        !help
        !help help"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 1:
            commands = []
            for name, command in bc.commands.data.items():
                if command.perform is None:
                    s = (name, command.message)
                    commands.append(s)
            commands.sort()
            version = bc.commands.config.get_version()
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
            name = command[1]
            if command[1] in bc.commands.data:
                command = bc.commands.data[command[1]]
            elif command[1] in bc.commands.aliases.keys():
                command = bc.commands.data[bc.commands.aliases[command[1]]]
            else:
                await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
                return
            result = name + ": "
            if command.perform is not None:
                result += command.get_actor().__doc__
            else:
                result += command.message
            result += '\n'
            result += "    Required permission level: {}\n".format(command.permission)
            if command.subcommand:
                result += "    This command can be used as subcommand\n"
            await Util.response(message, result, silent)

    @staticmethod
    async def _addcmd(message, command, silent=False):
        """Add command
    Example: !addcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            await Util.response(message, "Command {} already exists".format(command_name), silent)
            return
        bc.commands.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        bc.commands.data[command_name].channels.append(message.channel.id)
        await Util.response(message, "Command '{}' -> '{}' successfully added".format(
            command_name, bc.commands.data[command_name].message), silent)

    @staticmethod
    async def _updcmd(message, command, silent=False):
        """Update command (works only for commands that already exist)
    Example: !updcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if bc.commands.data[command_name].message is None:
                await Util.response(message, "Command '{}' is not editable".format(command_name), silent)
                return
            bc.commands.data[command_name].message = ' '.join(command[2:])
            await Util.response(message, "Command '{}' -> '{}' successfully updated".format(
                command_name, bc.commands.data[command_name].message), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    @staticmethod
    async def _delcmd(message, command, silent=False):
        """Delete command
    Example: !delcmd hello"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            bc.commands.data.pop(command_name, None)
            await Util.response(message, "Command '{}' successfully deleted".format(command_name), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    @staticmethod
    async def _enablecmd(message, command, silent=False):
        """Enable command in specified scope
    Examples:
        !enablecmd ping channel
        !enablecmd ping guild
        !enablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if command[2] == "channel":
                if message.channel.id not in bc.commands.data[command_name].channels:
                    bc.commands.data[command_name].channels.append(message.channel.id)
                await Util.response(message, "Command '{}' is enabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id not in bc.commands.data[command_name].channels:
                        bc.commands.data[command_name].channels.append(channel.id)
                await Util.response(message, "Command '{}' is enabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                bc.commands.data[command_name].is_global = True
                await Util.response(message, "Command '{}' is enabled in global scope".format(command_name), silent)
            else:
                await Util.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    @staticmethod
    async def _disablecmd(message, command, silent=False):
        """Disable command in specified scope
    Examples:
        !disablecmd ping channel
        !disablecmd ping guild
        !disablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if command[2] == "channel":
                if message.channel.id in bc.commands.data[command_name].channels:
                    bc.commands.data[command_name].channels.remove(message.channel.id)
                await Util.response(message, "Command '{}' is disabled in this channel".format(command_name), silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in bc.commands.data[command_name].channels:
                        bc.commands.data[command_name].channels.remove(channel.id)
                await Util.response(message, "Command '{}' is disabled in this guild".format(command_name), silent)
            elif command[2] == "global":
                bc.commands.data[command_name].is_global = False
                await Util.response(message, "Command '{}' is disabled in global scope".format(command_name), silent)
            else:
                await Util.response(message, "Unknown scope '{}'".format(command[2]), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    @staticmethod
    async def _permcmd(message, command, silent=False):
        """Set commands permission
    Example: !permcmd ping 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        perm = await Util.parse_int(message, command[2],
                                    "Third argument of command '{}' should be an integer".format(command[0]), silent)
        if perm is None:
            return
        if command_name in bc.commands.data.keys():
            bc.commands.data[command_name].permission = perm
            await Util.response(message, "Set permission level {} for command '{}'".format(
                command[2], command_name), silent)
            return
        await Util.response(message, "Command '{}' does not exist".format(command_name), silent)

    @staticmethod
    async def _timescmd(message, command, silent=False):
        """Print how many times command was invoked
    Example: !timescmd echo"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] in bc.config.commands.aliases.keys():
            command[1] = bc.config.commands.aliases[command[1]]
        if command[1] not in bc.commands.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        com = bc.commands.data[command[1]]
        await Util.response(message, "Command '{}' was invoked {} times".format(
            command[1],
            str(com.times_called if hasattr(com, "times_called") else 0)), silent)

    @staticmethod
    async def _permuser(message, command, silent=False):
        """Set user permission
    Example: !permcmd @nickname 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        perm = await Util.parse_int(message, command[2],
                                    "Third argument of command '{}' should be an integer".format(command[0]), silent)
        if perm is None:
            return
        user_id = int(command[1][2:-1])
        for user in bc.commands.config.users.keys():
            if bc.commands.config.users[user].id == user_id:
                bc.commands.config.users[user].permission_level = perm
                await Util.response(message, "User permissions are set to {}".format(command[2]), silent)
                return
        await Util.response(message, "User '{}' is not found".format(command[1]), silent)

    @staticmethod
    async def _whitelist(message, command, silent=False):
        """Bot's whitelist
    Examples:
        !whitelist enable/disable
        !whitelist add
        !whitelist remove"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] == "enable":
            bc.commands.config.guilds[message.channel.guild.id].is_whitelisted = True
            await Util.response(message, "This guild is whitelisted for bot", silent)
        elif command[1] == "disable":
            bc.commands.config.guilds[message.channel.guild.id].is_whitelisted = False
            await Util.response(message, "This guild is not whitelisted for bot", silent)
        elif command[1] == "add":
            bc.commands.config.guilds[message.channel.guild.id].whitelist.add(message.channel.id)
            await Util.response(message, "This channel is added to bot's whitelist", silent)
        elif command[1] == "remove":
            bc.commands.config.guilds[message.channel.guild.id].whitelist.discard(message.channel.id)
            await Util.response(message, "This channel is removed from bot's whitelist", silent)
        else:
            await Util.response(message, "Unknown argument '{}'".format(command[1]), silent)

    @staticmethod
    async def _config(message, command, silent=False):
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
                "enabled" if (message.channel.id
                              in bc.commands.config.guilds[message.channel.guild.id].reactions_whitelist)
                else "disabled")
            result += "Markov logging: {}\n".format(
                "enabled" if (message.channel.id
                              in bc.commands.config.guilds[message.channel.guild.id].markov_whitelist)
                else "disabled")
            result += "Markov responses: {}\n".format(
                "enabled" if (message.channel.id
                              in bc.commands.config.guilds[message.channel.guild.id].responses_whitelist)
                else "disabled")
            result += "Markov pings: {}\n".format(
                "enabled" if bc.commands.config.guilds[message.channel.guild.id].markov_pings
                else "disabled")
            await Util.response(message, result, silent)
        elif len(command) == 3:
            if command[1] == "reactions":
                if command[2] == "enable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].reactions_whitelist:
                        await Util.response(
                            message, "Adding reactions is already enabled for this channel", silent)
                    else:
                        bc.commands.config.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Adding reactions is successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].reactions_whitelist:
                        bc.commands.config.guilds[message.channel.guild.id].reactions_whitelist.discard(
                            message.channel.id)
                        await Util.response(
                            message, "Adding reactions is successfully disabled for this channel", silent)
                    else:
                        await Util.response(
                            message, "Adding reactions is already disabled for this channel", silent)
                else:
                    await Util.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovlog":
                if command[2] == "enable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].markov_whitelist:
                        await Util.response(
                            message, "Adding messages to Markov model is already enabled for this channel", silent)
                    else:
                        bc.commands.config.guilds[message.channel.guild.id].markov_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Adding messages to Markov model is successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].markov_whitelist:
                        bc.commands.config.guilds[message.channel.guild.id].markov_whitelist.discard(message.channel.id)
                        await Util.response(
                            message, "Adding messages to Markov model is successfully disabled for this channel",
                            silent)
                    else:
                        await Util.response(
                            message, "Adding messages to Markov model is already disabled for this channel", silent)
            elif command[1] == "responses":
                if command[2] == "enable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].responses_whitelist:
                        await Util.response(
                            message, "Bot responses on mentioning are already enabled for this channel", silent)
                    else:
                        bc.commands.config.guilds[message.channel.guild.id].responses_whitelist.add(message.channel.id)
                        await Util.response(
                            message, "Bot responses on mentioning are successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if message.channel.id in bc.commands.config.guilds[message.channel.guild.id].responses_whitelist:
                        bc.commands.config.guilds[message.channel.guild.id].responses_whitelist.discard(
                            message.channel.id)
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
                    if bc.commands.config.guilds[message.channel.guild.id].markov_pings:
                        await Util.response(
                            message, "Markov pings are already enabled for this channel", silent)
                    else:
                        bc.commands.config.guilds[message.channel.guild.id].markov_pings = True
                        await Util.response(
                            message, "Markov pings are successfully enabled for this channel", silent)
                elif command[2] == "disable":
                    if bc.commands.config.guilds[message.channel.guild.id].markov_pings:
                        bc.commands.config.guilds[message.channel.guild.id].markov_pings = False
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

    @staticmethod
    async def _addreaction(message, command, silent=False):
        """Add reaction
    Example: !addreaction emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        bc.commands.config.reactions.append(Reaction(' '.join(command[2:]), command[1]))
        await Util.response(message, "Reaction '{}' on '{}' successfully added".format(
            command[1], ' '.join(command[2:])), silent)

    @staticmethod
    async def _updreaction(message, command, silent=False):
        """Update reaction
    Example: !updreaction index emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should an index (integer)".format(command[0]), silent)
        if index is None:
            return
        if not 0 <= index < len(bc.commands.config.reactions):
            await Util.response(message, "Incorrect index of reaction!", silent)
            return
        bc.commands.config.reactions[index] = Reaction(' '.join(command[3:]), command[2])
        await Util.response(message, "Reaction '{}' on '{}' successfully updated".format(
            command[1], ' '.join(command[2:])), silent)

    @staticmethod
    async def _delreaction(message, command, silent=False):
        """Delete reaction
    Examples:
        !delreaction emoji
        !delreaction index"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = -1
        try:
            index = int(command[1])
            if not 0 <= index < len(bc.commands.config.reactions):
                await Util.response(message, "Incorrect index of reaction!", silent)
                return
            reaction = bc.commands.config.reactions[index]
            bc.commands.config.reactions.pop(index)
            await Util.response(message, "Reaction '{}' -> '{}' successfully removed".format(
                reaction.regex, reaction.emoji), silent)
        except Exception:
            i = 0
            while i < len(bc.commands.config.reactions):
                if bc.commands.config.reactions[i].emoji == command[1]:
                    bc.commands.config.reactions.pop(i)
                else:
                    i += 1
            await Util.response(message, "Reaction '{}' successfully removed".format(command[1]), silent)

    @staticmethod
    async def _listreaction(message, command, silent=False):
        """Print list of reactions
    Example: !listreaction"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, reaction in enumerate(bc.commands.config.reactions):
            result += "{} - {}: {}\n".format(index, reaction.emoji, reaction.regex)
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reactions found!", silent)
        return result

    @staticmethod
    async def _wme(message, command, silent=False):
        """Send direct message to author with something
    Example: !wme Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[1:])
        if not result:
            return
        result = "You asked me to send you this: " + result
        await Util.send_direct_message(message, result, silent)

    @staticmethod
    async def _poll(message, command, silent=False):
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

    @staticmethod
    async def _version(message, command, silent=False):
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        result = bc.commands.config.get_version()
        if len(command) == 2 and (command[1] == 's' or command[1] == 'short'):
            result = result[:7]
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _about(message, command, silent=False):
        """Get information about the bot
    Example: !about"""
        result = str(bc.bot_user) + ' (WalBot instance)\n'
        result += "Source code: <https://github.com/aobolensk/walbot>\n"
        result += "Version: " + bc.commands.config.get_version() + '\n'
        result += "Uptime: " + bc.commands.config.get_uptime() + '\n'
        await Util.response(message, result, silent)

    @staticmethod
    async def _addbgevent(message, command, silent=False):
        """Add background event
    Example: !addbgevent 60 ping"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        duration = await Util.parse_int(message, command[1],
                                        "Second parameter for '{}' should be duration in seconds".format(command[0]),
                                        silent)
        if duration is None:
            return
        message.content = bc.commands.config.commands_prefix + ' '.join(command[2:])
        bc.background_events.append(BackgroundEvent(
            bc.commands.config, message.channel, message, duration))
        await Util.response(message, "Successfully added background event '{}' with period {}".format(
                            message.content, str(duration)), silent)

    @staticmethod
    async def _listbgevent(message, command, silent=False):
        """Print list of background events
    Example: !listbgevent"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, event in enumerate(bc.background_events):
            result += "{}: '{}' every {} seconds, channel: {}\n".format(
                str(index), event.message.content, str(event.period), "<#{}>".format(event.channel.id))
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No background events found!", silent)
        return result

    @staticmethod
    async def _delbgevent(message, command, silent=False):
        """Delete background event
    Example: !delbgevent 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of background event"
                                     .format(command[0]), silent)
        if index is None:
            return
        if 0 <= index < len(bc.background_events):
            bc.background_events[index].cancel()
            del bc.background_events[index]
            await Util.response(message, "Successfully deleted background task!", silent)
        else:
            await Util.response(message, "Invalid index of background task!", silent)

    @staticmethod
    async def _random(message, command, silent=False):
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

    @staticmethod
    async def _randselect(message, command, silent=False):
        """Get random option among provided strings
    Example: !randselect a b c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        index = random.randint(1, len(command) - 1)
        result = command[index]
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _silent(message, command, silent=False):
        """Make the following command silent (without any output to the chat)
    Example: !silent ping"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        command = command[1:]
        if command[0] not in bc.commands.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[0]), silent)
        else:
            cmd = bc.commands.data[command[0]]
            await cmd.run(message, command, None, silent=True)

    @staticmethod
    async def _time(message, command, silent=False):
        """Show current time
    Example: !time"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = str(datetime.datetime.now()).split('.')[0]
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _uptime(message, command, silent=False):
        """Show bot uptime
    Example: !uptime"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.commands.config.get_uptime()
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _status(message, command, silent=False):
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

    @staticmethod
    async def _channelid(message, command, silent=False):
        """Get channel ID
    Example: !channelid"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = str(message.channel.id)
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _addalias(message, command, silent=False):
        """Add alias for commands
    Usage: !addalias <command> <alias>
    Example: !addalias ping pong"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        if command[1] not in bc.commands.data.keys():
            await Util.response(message, "Unknown command '{}'".format(command[1]), silent)
            return
        if command[2] in bc.commands.data.keys():
            await Util.response(message, "Command '{}' already exists".format(command[2]), silent)
            return
        if command[2] in bc.commands.aliases.keys():
            await Util.response(message, "Alias '{}' already exists".format(command[2]), silent)
            return
        bc.commands.aliases[command[2]] = command[1]
        await Util.response(message, "Alias '{}' for '{}' was successfully created".format(
            command[2], command[1]), silent)

    @staticmethod
    async def _delalias(message, command, silent=False):
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

    @staticmethod
    async def _listalias(message, command, silent=False):
        """Print list of aliases
    Example: !listalias"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for alias, command in bc.commands.aliases.items():
            result += alias + " -> " + command + '\n'
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _markov(message, command, silent=False):
        """Generate message using Markov chain
    Example: !markov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = await bc.commands.config.disable_pings_in_response(message, bc.markov.generate())
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _markovgc(message, command, silent=False):
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.markov.gc()
        result = "Garbage collected {} items: {}".format(len(result), ', '.join(result))
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _delmarkov(message, command, silent=False):
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        removed = bc.markov.del_words(regex)
        await Util.response(message, "Deleted {} words from model: {}".format(str(len(removed)),
                            str(removed)), silent, suppress_embeds=True)

    @staticmethod
    async def _findmarkov(message, command, silent=False):
        """Match words in Markov model using regex
    Example: !findmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        found = bc.markov.find_words(regex)
        await Util.response(message, "Found {} words in model: {}".format(str(len(found)),
                            str(found)), silent, suppress_embeds=True)

    @staticmethod
    async def _dropmarkov(message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        bc.markov.__init__()
        await Util.response(message, "Markov database has been dropped!", silent)

    @staticmethod
    async def _addmarkovfilter(message, command, silent=False):
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        bc.markov.filters.append(re.compile(command[1]))
        await Util.response(message, "Filter '{}' was successfully added for Markov model".format(command[1]), silent)

    @staticmethod
    async def _listmarkovfilter(message, command, silent=False):
        """Print list of regular expression filters for Markov model
    Example: !listmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, regex in enumerate(bc.markov.filters):
            result += "{} -> {}\n".format(index, regex.pattern)
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No filters for Markov model found!", silent)
        return result

    @staticmethod
    async def _delmarkovfilter(message, command, silent=False):
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
        if 0 <= index < len(bc.markov.filters):
            bc.markov.filters.pop(index)
            await Util.response(message, "Successfully deleted filter!", silent)
        else:
            await Util.response(message, "Invalid index of filter!", silent)

    @staticmethod
    async def _img(message, command, silent=False):
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
                        await Util.response(message, "Image {} is not found!".format(command[i]), silent)
                    break

    @staticmethod
    async def _wmeimg(message, command, silent=False):
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

    @staticmethod
    async def _listimg(message, command, silent=False):
        """Print list of available images for !img command
    Example: !listimg"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = []
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    result.append(os.path.splitext(os.path.basename(file))[0])
        result.sort()
        if result:
            await Util.response(message, "List of available images: [" + ', '.join(result) + "]", silent)
        else:
            await Util.response(message, "No available images found!", silent)

    @staticmethod
    async def _addimg(message, command, silent=False):
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

    @staticmethod
    async def _delimg(message, command, silent=False):
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

    @staticmethod
    async def _tts(message, command, silent=False):
        """Send text-to-speech (TTS) message
    Example: !tts Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        text = ' '.join(command[1:])
        await Util.response(message, text, silent, tts=True)
        log.debug("Sent TTS message: {}".format(text))

    @staticmethod
    async def _urlencode(message, command, silent=False):
        """Urlencode string
    Example: !urlencode hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[1:])
        result = urllib.request.quote(result.encode("cp1251"))
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _emojify(message, command, silent=False):
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

    @staticmethod
    async def _demojify(message, command, silent=False):
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

    @staticmethod
    async def _shutdown(message, command, silent=False):
        """Shutdown the bot
    Example: !shutdown"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        log.info(str(message.author) + " invoked shutting down the bot")
        await bc.close()

    @staticmethod
    async def _avatar(message, command, silent=False):
        """Change bot avatar
    Example: !avatar <image>
    Hint: Use !listimg for list of available images"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        for root, _, files in os.walk("images"):
            if root.endswith("images"):
                for file in files:
                    if os.path.splitext(os.path.basename(file))[0] == command[1]:
                        try:
                            with open(os.path.join("images", file), "rb") as f:
                                await bc.bot_user.edit(avatar=f.read())
                            await Util.response(message,
                                                "Successfully changed bot avatar to {}".format(command[1]), silent)
                        except discord.HTTPException as e:
                            await Util.response(message,
                                                "Failed to change bot avatar.\nError: {}".format(e), silent)
                        return
        await Util.response(message, "Image {} is not found!".format(command[1]), silent)

    @staticmethod
    async def _message(message, command, silent=False):
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

    @staticmethod
    async def _reminder(message, command, silent=False):
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
                                    time, const.REMINDER_TIME_FORMAT), silent)
            return
        text = ' '.join(command[3:])
        bc.commands.config.reminders.append(Reminder(str(time), text, message.channel.id))
        await Util.response(message, "Reminder '{}' added at {}".format(text, time), silent)

    @staticmethod
    async def _updreminder(message, command, silent=False):
        """Update reminder by index
    Example: !delreminder 0 2020-01-01 00:00 Happy new year!"""
        if not await Util.check_args_count(message, command, silent, min=5):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of reminder"
                                     .format(command[0]), silent)
        if index is None:
            return
        if 0 <= index < len(bc.commands.config.reminders):
            time = command[2] + ' ' + command[3]
            try:
                time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
            except ValueError:
                await Util.response(message, "{} does not match format {}\n"
                                    "More information about format: <https://strftime.org/>".format(
                                        time, const.REMINDER_TIME_FORMAT), silent)
                return
            text = ' '.join(command[4:])
            bc.commands.config.reminders[index] = Reminder(str(time), text, message.channel.id)
            await Util.response(message, "Successfully updated reminder {}: '{}' at {}".format(
                                    index, text, time), silent)
        else:
            await Util.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _listreminder(message, command, silent=False):
        """Print list of reminders
    Example: !listreminder"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        result = ""
        reminders = sorted(zip(range(0, len(bc.commands.config.reminders)), bc.commands.config.reminders),
                           key=lambda x: x[1])
        for index, reminder in reminders:
            result += "{} - {} in {} -> {}\n".format(
                index, reminder.time, "<#{}>".format(reminder.channel_id), reminder.message)
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reminders found!", silent)
        return result

    @staticmethod
    async def _delreminder(message, command, silent=False):
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
        if 0 <= index < len(bc.commands.config.reminders):
            bc.commands.config.reminders.pop(index)
            await Util.response(message, "Successfully deleted reminder!", silent)
        else:
            await Util.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _server(message, command, silent=False):
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

    @staticmethod
    async def _quote(message, command, silent=False):
        """Print some quote from quotes database
    Examples:
        !quote
        !quote 1"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if not bc.commands.config.quotes:
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
            index = random.randint(0, len(bc.commands.config.quotes) - 1)
        if 0 <= index < len(bc.commands.config.quotes):
            await Util.response(message,
                                "Quote {}: {}".format(index, bc.commands.config.quotes[index].full_quote()), silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)

    @staticmethod
    async def _addquote(message, command, silent=False):
        """Add quote to quotes database
    Example: !addquote Hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        quote = ' '.join(command[1:])
        bc.commands.config.quotes.append(Quote(quote, str(message.author)))
        await Util.response(message,
                            "Quote '{}' was successfully added to quotes database with index {}".format(
                                quote, len(bc.commands.config.quotes) - 1), silent)

    @staticmethod
    async def _listquote(message, command, silent=False):
        """Print list of all quotes
    Example: !listquote"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, quote in enumerate(bc.commands.config.quotes):
            result += "{} -> {}\n".format(index, quote.quote())
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "<Quotes database is empty>", silent)
        return result

    @staticmethod
    async def _delquote(message, command, silent=False):
        """Delete quote from quotes database by index
    Example: !delquote 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of quote"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if 0 <= index < len(bc.commands.config.quotes):
            bc.commands.config.quotes.pop(index)
            await Util.response(message, "Successfully deleted quote!", silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)

    @staticmethod
    async def _setquoteauthor(message, command, silent=False):
        """Set author of quote by its index
    Example: !setquoteauthor 0 WalBot"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of quote"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if 0 <= index < len(bc.commands.config.quotes):
            author = ' '.join(command[2:])
            bc.commands.config.quotes[index].author = author
            await Util.response(message,
                                "Successfully set author '{}' for quote '{}'".format(
                                    author, bc.commands.config.quotes[index].quote()), silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)
