import asyncio
import base64
import datetime
import imghdr
import os
import random
import re
import shutil
import tempfile
import urllib.request

import discord
import requests
from dateutil import tz

from src import const, emoji
from src.algorithms import levenshtein_distance
from src.commands import BaseCmd
from src.config import BackgroundEvent, Command, bc, log
from src.message import Msg
from src.utils import Util, null


class _BuiltinInternals:
    @staticmethod
    async def get_image(message, command, silent):
        for i in range(1, len(command)):
            for root, _, files in os.walk(const.IMAGES_DIRECTORY):
                if not root.endswith(const.IMAGES_DIRECTORY):
                    continue
                for file in files:
                    if not silent and os.path.splitext(os.path.basename(file))[0].lower() == command[i].lower():
                        await Msg.response(message, None, silent,
                                           files=[discord.File(os.path.join(const.IMAGES_DIRECTORY, file))])
                        break
                else:
                    # Custom emoji
                    r = const.EMOJI_REGEX.match(command[i])
                    if r is not None:
                        await Msg.response(message, f"https://cdn.discordapp.com/emojis/{r.group(2)}.png", silent)
                        break
                    # Unicode emoji
                    if const.UNICODE_EMOJI_REGEX.match(command[i]):
                        emojis_page = requests.get('https://unicode.org/emoji/charts/full-emoji-list.html').text
                        emoji_match = r"<img alt='{}' class='imga' src='data:image/png;base64,([^']+)'>"
                        emoji_match = re.findall(emoji_match.format(command[i]), emojis_page)
                        if emoji_match:
                            os.makedirs(Util.tmp_dir(), exist_ok=True)
                            temp_image_file = tempfile.NamedTemporaryFile(dir=Util.tmp_dir())
                            with open(temp_image_file.name, 'wb') as f:
                                f.write(base64.b64decode(emoji_match[4]))  # Twemoji is located under the 4th number
                            shutil.copy(temp_image_file.name, temp_image_file.name + ".png")
                            await Msg.response(
                                message, None, silent, files=[discord.File(temp_image_file.name + ".png")])
                            os.unlink(temp_image_file.name + ".png")
                            break
                    min_dist = 100000
                    suggestion = ""
                    for file in (os.path.splitext(os.path.basename(file))[0].lower() for file in files):
                        dist = levenshtein_distance(command[i], file)
                        if dist < min_dist:
                            suggestion = file
                            min_dist = dist
                    await Msg.response(
                        message,
                        f"Image '{command[i]}' is not found! "
                        f"Probably you meant '{suggestion}'",
                        silent)
                break


class BuiltinCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "takechars",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "dropchars",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "countchars",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "takewords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "dropwords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "countwords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "takelines",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "droplines",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "countlines",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "tolower",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "toupper",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "join",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "range",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "ping",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "help",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "profile",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addextcmd",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "updcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "updextcmd",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delcmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "enablecmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "disablecmd",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "permcmd",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "timescmd",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "permuser",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "extexec",
                                     permission=const.Permission.ADMIN.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "whitelist",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "config",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "wme",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "poll",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "version",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "about",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addbgevent",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listbgevent",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "delbgevent",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "random",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "randselect",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "randselects",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "eqwords",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "eqstrs",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "silent",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "time",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "uptime",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "status",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "channelid",
                                     permission=const.Permission.MOD.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "addalias",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delalias",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listalias",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "img",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listimg",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addimg",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delimg",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "tts",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "urlencode",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "emojify",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "demojify",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "shutdown",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "restart",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "avatar",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "message",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "server",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "pin",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "slowmode",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "curl",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "nick",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "reloadbotcommands",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "echo",
                                     message="@args@",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "code",
                                     message="`@args@`",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "permlevel",
                                     permission=const.Permission.USER.value, subcommand=False)

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
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = result[len(result) + num:]
        else:
            result = result[:num]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _dropchars(message, command, silent=False):
        """Drop n characters of the string
    Examples:
        !dropchars 2 hello
        Result: llo
        !dropchars -2 hello
        Result: hel"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:])
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = result[:len(result) + num]
        else:
            result = result[num:]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countchars(message, command, silent=False):
        """Calculate length of the message
    Example: !countchars some text"""
        result = str(len(' '.join(command[1:])))
        await Msg.response(message, result, silent)
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
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[len(result) + num:])
        else:
            result = ' '.join(result[:num])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _dropwords(message, command, silent=False):
        """Drop n words of the string
    Examples:
        !dropwords 2 a b c
        Result: c
        !dropwords -2 a b c
        Result: a"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split()
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[:len(result) + num])
        else:
            result = ' '.join(result[num:])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countwords(message, command, silent=False):
        """Count amount of words
    Example: !count some text"""
        result = str(len(' '.join(command).split()) - 1)
        await Msg.response(message, result, silent)
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
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[len(result) + num:])
        else:
            result = '\n'.join(result[:num])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _droplines(message, command, silent=False):
        """Drop n lines of the string
    Examples:
        !droplines 2 a
        b
        c
        Result: c
        !droplines -2 a
        b
        c
        Result: a"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split('\n')
        num = await Util.parse_int(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[:len(result) + num])
        else:
            result = '\n'.join(result[num:])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countlines(message, command, silent=False):
        """Count amount of lines
    Example: !count some text"""
        result = str(len(' '.join(command).split('\n')))
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _tolower(message, command, silent=False):
        """Convert text to lower case
    Example: !tolower SoMe TeXt"""
        result = ' '.join(command[1:]).lower()
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _toupper(message, command, silent=False):
        """Convert text to upper case
    Example: !toupper SoMe TeXt"""
        result = ' '.join(command[1:]).upper()
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _join(message, command, silent=False):
        """Join words with string as separator
    Example: !join + 1 2 3 -> 1+2+3"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        separator = command[1]
        result = separator.join(command[2:])
        await Msg.response(message, result, silent)
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
            stop = await Util.parse_int(
                message, command[1], f"Stop parameter in range '{command[0]}' should be an integer", silent)
        else:
            start = await Util.parse_int(
                message, command[1], f"Start parameter in range '{command[0]}' should be an integer", silent)
            stop = await Util.parse_int(
                message, command[2], f"Stop parameter in range '{command[0]}' should be an integer", silent)
            if len(command) == 4:
                step = await Util.parse_int(
                    message, command[3], f"Step parameter in range '{command[0]}' should be an integer", silent)
        if start is None or stop is None or step is None:
            return
        result = ''
        for iteration, number in enumerate(range(start, stop, step)):
            if iteration >= const.MAX_RANGE_ITERATIONS:
                result = f"Range iteration limit ({const.MAX_RANGE_ITERATIONS}) has exceeded"
                break
            result += str(number) + ' '
        else:
            result = result[:-1]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _ping(message, command, silent=False):
        """Check whether the bot is active and get latency in ms
    Example: !ping"""
        result = f":ping_pong: Pong! {message.author.mention} :ping_pong:\n"
        result += f"Latency: {round(bc.latency() * 1000)} ms"
        await Msg.response(message, result, silent)

    @staticmethod
    async def _profile(message, command, silent=False):
        """Print information about user
    Examples:
        !profile
        !profile `@user`"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        info = ""
        if len(command) == 1:
            info = message.author
        elif len(command) == 2:
            if not message.mentions:
                return null(
                    await Msg.response(message, "You need to mention the user you want to get profile of", silent))
            info = await message.guild.fetch_member(message.mentions[0].id)
        if info is None:
            return null(await Msg.response(message, "Could not get information about this user", silent))
        roles = ', '.join([x if x != const.ROLE_EVERYONE else const.ROLE_EVERYONE[1:] for x in map(str, info.roles)])
        result = (f"{message.author.mention}\n"
                  f"User: {f'{info.nick} ({info})'if info.nick is not None else info}\n"
                  f"Avatar: <{info.avatar_url}>\n"
                  f"Created at: {info.created_at}\n"
                  f"Joined this server at: {info.joined_at}\n"
                  f"Roles: {roles}\n")
        await Msg.response(message, result, silent)

    @staticmethod
    async def _help(message, command, silent=False):
        """Print list of commands and get examples
    Examples:
        !help
        !help -p
        !help help"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 1 or (len(command) == 2 and command[1] == '-p'):
            commands = []
            for name, cmd in bc.commands.data.items():
                if cmd.message is not None:
                    s = (name, cmd.message)
                    commands.append(s)
                elif cmd.cmd_line is not None:
                    s = (name, f"calls external command `{cmd.cmd_line}`")
                    commands.append(s)
                elif cmd.is_private:
                    s = (name, "*Private command*\n" + cmd.get_actor().__doc__)
                    commands.append(s)
            commands.sort()
            version = bc.info.version
            if len(command) == 2 and command[1] == '-p':
                # Plain text help
                result = (f"Built-in commands <{const.GIT_REPO_LINK}/blob/" +
                          (version if version != ' ' else "master") + "/" + const.COMMANDS_DOC_PATH + ">\n")
                for cmd in commands:
                    result += f"**{cmd[0]}**: {cmd[1]}\n"
                await Msg.response(message, result, silent, suppress_embeds=True)
            else:
                # Embed help
                commands.insert(
                    0, ("Built-in commands", (
                        f"<{const.GIT_REPO_LINK}/blob/" +
                        (version if version != ' ' else "master") + "/" + const.COMMANDS_DOC_PATH + ">")))
                for chunk in Msg.split_by_chunks(commands, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
                    embed = discord.Embed(title="Help", color=0x717171)
                    for cmd in chunk:
                        cmd_name = cmd[0]
                        description = cmd[1]
                        if len(description) > 1024:
                            description = description[:1021] + "..."
                        embed.add_field(name=cmd_name, value=description, inline=False)
                    await Msg.response(message, None, silent, embed=embed)
        elif len(command) == 2:
            name = command[1]
            if command[1] in bc.commands.data:
                command = bc.commands.data[command[1]]
            elif command[1] in bc.commands.aliases.keys():
                command = bc.commands.data[bc.commands.aliases[command[1]]]
            else:
                return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
            result = name + ": "
            if command.perform is not None:
                result += command.get_actor().__doc__
            elif command.message is not None:
                result += "`" + command.message + "`"
            elif command.cmd_line is not None:
                result += f"calls external command `{command.cmd_line}`"
            else:
                result += "<error>"
            result += '\n'
            result += f"    Required permission level: {command.permission}\n"
            if command.subcommand:
                result += "    This command can be used as subcommand\n"
            await Msg.response(message, result, silent)

    @staticmethod
    async def _addcmd(message, command, silent=False):
        """Add command
    Example: !addcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            return null(await Msg.response(message, f"Command {command_name} already exists", silent))
        bc.commands.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        bc.commands.data[command_name].channels.append(message.channel.id)
        await Msg.response(
            message, f"Command '{command_name}' -> '{bc.commands.data[command_name].message}' successfully added",
            silent)

    @staticmethod
    async def _addextcmd(message, command, silent=False):
        """Add command that executes external process
    Note: Be careful when you are executing external commands!
    Example: !addextcmd uname uname -a"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            return null(await Msg.response(message, f"Command {command_name} already exists", silent))
        bc.commands.data[command_name] = Command(command_name, cmd_line=' '.join(command[2:]))
        bc.commands.data[command_name].channels.append(message.channel.id)
        await Msg.response(
            message, f"Command '{command_name}' that calls external command "
                     f"`{bc.commands.data[command_name].cmd_line}` is successfully added", silent)

    @staticmethod
    async def _updcmd(message, command, silent=False):
        """Update command (works only for commands that already exist)
    Example: !updcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if bc.commands.data[command_name].message is None:
                return null(await Msg.response(message, f"Command '{command_name}' is not editable", silent))
            bc.commands.data[command_name].message = ' '.join(command[2:])
            return null(
                await Msg.response(
                    message, f"Command '{command_name}' -> "
                             f"'{bc.commands.data[command_name].message}' successfully updated", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _updextcmd(message, command, silent=False):
        """Update command that executes external process (works only for commands that already exist)
    Note: Be careful when you are executing external commands!
    Example: !updextcmd uname uname -a"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if bc.commands.data[command_name].cmd_line is None:
                return null(await Msg.response(message, f"Command '{command_name}' is not editable", silent))
            bc.commands.data[command_name].cmd_line = ' '.join(command[2:])
            return null(
                await Msg.response(
                    message, f"Command '{command_name}' that calls external command "
                             f"`{bc.commands.data[command_name].cmd_line}` is successfully updated", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _delcmd(message, command, silent=False):
        """Delete command
    Example: !delcmd hello"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            bc.commands.data.pop(command_name, None)
            return null(await Msg.response(message, f"Command '{command_name}' successfully deleted", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _enablecmd(message, command, silent=False):
        """Enable command in specified scope
    Examples:
        !enablecmd ping
        !enablecmd ping channel
        !enablecmd ping guild
        !enablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if len(command) == 2 or command[2] == "channel":
                if message.channel.id not in bc.commands.data[command_name].channels:
                    bc.commands.data[command_name].channels.append(message.channel.id)
                await Msg.response(message, f"Command '{command_name}' is enabled in this channel", silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id not in bc.commands.data[command_name].channels:
                        bc.commands.data[command_name].channels.append(channel.id)
                await Msg.response(message, f"Command '{command_name}' is enabled in this guild", silent)
            elif command[2] == "global":
                bc.commands.data[command_name].is_global = True
                await Msg.response(message, f"Command '{command_name}' is enabled in global scope", silent)
            else:
                await Msg.response(message, f"Unknown scope '{command[2]}'", silent)
            return
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _disablecmd(message, command, silent=False):
        """Disable command in specified scope
    Examples:
        !disablecmd ping
        !disablecmd ping channel
        !disablecmd ping guild
        !disablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        command_name = command[1]
        if command_name in bc.commands.data.keys():
            if len(command) == 2 or command[2] == "channel":
                if message.channel.id in bc.commands.data[command_name].channels:
                    bc.commands.data[command_name].channels.remove(message.channel.id)
                await Msg.response(message, f"Command '{command_name}' is disabled in this channel", silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in bc.commands.data[command_name].channels:
                        bc.commands.data[command_name].channels.remove(channel.id)
                await Msg.response(message, f"Command '{command_name}' is disabled in this guild", silent)
            elif command[2] == "global":
                bc.commands.data[command_name].is_global = False
                await Msg.response(message, f"Command '{command_name}' is disabled in global scope", silent)
            else:
                await Msg.response(message, f"Unknown scope '{command[2]}'", silent)
            return
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _permcmd(message, command, silent=False):
        """Set commands permission
    Example: !permcmd ping 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        perm = await Util.parse_int(
            message, command[2], f"Third argument of command '{command[0]}' should be an integer", silent)
        if perm is None:
            return
        if command_name in bc.commands.data.keys():
            bc.commands.data[command_name].permission = perm
            return null(
                await Msg.response(
                    message, f"Set permission level {command[2]} for command '{command_name}'", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _timescmd(message, command, silent=False):
        """Print how many times command was invoked
    Examples:
        !timescmd echo
        !timescmd echo -s"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        if command[1] in bc.config.commands.aliases.keys():
            command[1] = bc.config.commands.aliases[command[1]]
        if command[1] not in bc.commands.data.keys():
            return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
        com = bc.commands.data[command[1]]
        times = com.times_called
        if len(command) == 3 and command[2] == '-s':
            result = f"{times}"
        else:
            result = f"Command '{command[1]}' was invoked {times} times"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _permuser(message, command, silent=False):
        """Set user permission
    Example: !permuser @nickname 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        perm = await Util.parse_int(
            message, command[2], f"Third argument of command '{command[0]}' should be an integer", silent)
        if perm is None:
            return
        r = const.USER_ID_REGEX.search(command[1])
        if r is None:
            return null(
                await Msg.response(
                    message, f"Second argument of command '{command[0]}' should be user ping", silent))
        user_id = int(r.group(1))
        for user in bc.config.users.keys():
            if bc.config.users[user].id == user_id:
                bc.config.users[user].permission_level = perm
                return null(
                    await Msg.response(message, f"User permissions are set to {command[2]}", silent))
        await Msg.response(message, f"User '{command[1]}' is not found", silent)

    @staticmethod
    async def _extexec(message, command, silent=False):
        """Execute external shell command
    Note: Be careful when you are executing external commands!
    Example: !extexec uname -a"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        return await Util.run_external_command(message, ' '.join(command[1:]), silent)

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
            bc.config.guilds[message.channel.guild.id].is_whitelisted = True
            await Msg.response(message, "This guild is whitelisted for bot", silent)
        elif command[1] == "disable":
            bc.config.guilds[message.channel.guild.id].is_whitelisted = False
            await Msg.response(message, "This guild is not whitelisted for bot", silent)
        elif command[1] == "add":
            bc.config.guilds[message.channel.guild.id].whitelist.add(message.channel.id)
            await Msg.response(message, "This channel is added to bot's whitelist", silent)
        elif command[1] == "remove":
            bc.config.guilds[message.channel.guild.id].whitelist.discard(message.channel.id)
            await Msg.response(message, "This channel is removed from bot's whitelist", silent)
        else:
            await Msg.response(message, f"Unknown argument '{command[1]}'", silent)

    @staticmethod
    async def _config(message, command, silent=False):
        """Setup some channel specific configurations
    Examples:
        !config reactions <enable/disable>
        !config markovlog <enable/disable>
        !config responses <enable/disable>
        !config markovresponses <enable/disable>
        !config markovpings <enable/disable>"""
        if not await Util.check_args_count(message, command, silent, min=1, max=3):
            return
        if len(command) == 1:
            result = "Config:\n"
            result += "Emoji reactions on messages (reactions): " + (
                'enabled' if (message.channel.id in bc.config.guilds[message.channel.guild.id].reactions_whitelist)
                else 'disabled') + "\n"
            result += "Logging the messages to Markov model (markovlog): " + (
                'enabled' if (message.channel.id in bc.config.guilds[message.channel.guild.id].markov_logging_whitelist)
                else 'disabled') + "\n"
            result += "Text message responses on messages (responses): " + (
                'enabled' if (message.channel.id in bc.config.guilds[message.channel.guild.id].responses_whitelist)
                else 'disabled') + "\n"
            result += "Responses with random generated message using Markov model on mention (markovresponses): " + (
                'enabled' if (message.channel.id in
                              bc.config.guilds[message.channel.guild.id].markov_responses_whitelist)
                else 'disabled') + "\n"
            result += "Users pings in random generated messages using Markov model (markovpings): " + (
                'enabled' if bc.config.guilds[message.channel.guild.id].markov_pings
                else 'disabled') + "\n"
            await Msg.response(message, result, silent)
        elif len(command) == 3:
            if command[1] == "reactions":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].reactions_whitelist:
                        await Msg.response(
                            message, "Adding reactions is already enabled for this channel", silent)
                    else:
                        bc.config.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Adding reactions is successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].reactions_whitelist:
                        bc.config.guilds[message.channel.guild.id].reactions_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Adding reactions is successfully disabled for this channel", silent)
                    else:
                        await Msg.response(
                            message, "Adding reactions is already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovlog":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].markov_logging_whitelist:
                        await Msg.response(
                            message, "Adding messages to Markov model is already enabled for this channel", silent)
                    else:
                        bc.config.guilds[message.channel.guild.id].markov_logging_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Adding messages to Markov model is successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].markov_logging_whitelist:
                        bc.config.guilds[message.channel.guild.id].markov_logging_whitelist.discard(message.channel.id)
                        await Msg.response(
                            message, "Adding messages to Markov model is successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Adding messages to Markov model is already disabled for this channel", silent)
            elif command[1] == "responses":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].responses_whitelist:
                        await Msg.response(
                            message, "Bot responses are already enabled for this channel", silent)
                    else:
                        bc.config.guilds[message.channel.guild.id].responses_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Bot responses are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].responses_whitelist:
                        bc.config.guilds[message.channel.guild.id].responses_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Bot responses are successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Bot responses are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovresponses":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].markov_responses_whitelist:
                        await Msg.response(
                            message, "Bot responses on mentioning are already enabled for this channel", silent)
                    else:
                        bc.config.guilds[message.channel.guild.id].markov_responses_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Bot responses on mentioning are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.guilds[message.channel.guild.id].markov_responses_whitelist:
                        bc.config.guilds[message.channel.guild.id].markov_responses_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Bot responses on mentioning are successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Bot responses on mentioning are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovpings":
                if command[2] in ("enable", "true", "on"):
                    if bc.config.guilds[message.channel.guild.id].markov_pings:
                        await Msg.response(
                            message, "Markov pings are already enabled for this channel", silent)
                    else:
                        bc.config.guilds[message.channel.guild.id].markov_pings = True
                        await Msg.response(
                            message, "Markov pings are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if bc.config.guilds[message.channel.guild.id].markov_pings:
                        bc.config.guilds[message.channel.guild.id].markov_pings = False
                        await Msg.response(
                            message, "Markov pings are successfully disabled for this channel", silent)
                    else:
                        await Msg.response(
                            message, "Markov pings are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            else:
                await Msg.response(message, f"Incorrect argument for command '{command[0]}'", silent)
        else:
            await Msg.response(message, f"Incorrect usage of command '{command[0]}'", silent)

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
        await Msg.send_direct_message(message.author, result, silent)

    @staticmethod
    async def _poll(message, command, silent=False):
        """Create poll
    Example: !poll 60 option 1;option 2;option 3"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        if silent:
            return
        duration = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be duration in seconds", silent)
        if duration is None:
            return
        options = ' '.join(command[2:])
        options = options.split(';')
        if len(options) > const.MAX_POLL_OPTIONS:
            return null(
                await Msg.response(
                    message,
                    f"Too many options for poll (got: {len(options)}, max: {const.MAX_POLL_OPTIONS})", silent))
        poll_message = "Poll is started! You have " + command[1] + " seconds to vote!\n"
        for i in range(len(options)):
            poll_message += emoji.alphabet[i] + " -> " + options[i] + '\n'
        poll_message = await Msg.response(message, poll_message, silent)
        for i in range(len(options)):
            try:
                await poll_message.add_reaction(emoji.alphabet[i])
            except Exception:
                log.debug(f"Error on add_reaction: {emoji.alphabet[i]}")
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
                await Msg.response(message, f"Poll is still going! {remaining} seconds left", silent)
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
                await Msg.response(message, result_message, silent)
                for i in range(len(options)):
                    try:
                        await poll_message.remove_reaction(emoji.alphabet[i], poll_message.author)
                    except Exception:
                        log.debug(f"Error on remove_reaction: {emoji.alphabet[i]}")
                return

    @staticmethod
    async def _version(message, command, silent=False):
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        result = bc.info.version
        if len(command) == 2 and (command[1] == 's' or command[1] == 'short'):
            result = result[:7]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _about(message, command, silent=False):
        """Get information about the bot
    Examples:
        !about
        !about -v"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if not hasattr(bc, "bot_user"):
            return null(await Msg.response(message, "Bot is not loaded yet!", silent))
        result = (
            f"{bc.bot_user} (WalBot instance)\n"
            f"Source code: <{const.GIT_REPO_LINK}>\n"
            f"Version: {bc.info.version}{'-dirty' if bc.info.is_version_dirty else ''} "
            f"(updated at {bc.info.version_time})\n"
            f"Uptime: {bc.info.uptime}\n"
        )
        if len(command) > 1 and command[1] == "-v":
            result += (
                f"Deployment time: {bc.deployment_time}\n"
                f"Commit name: {bc.info.commit_name}\n"
                f"Branch name: {bc.info.branch_name}\n"
            )
            # Dependencies info
            result += "Dependencies:\n"
            result += '\n'.join(f"    {name}: {ver}" for name, ver in bc.info.query_dependencies_info().items())
        elif len(command) > 1:
            return null(
                await Msg.response(
                    message, f"Unknown argument '{command[1]}' for '{command[0]}' command", silent))
        await Msg.response(message, result, silent)

    @staticmethod
    async def _addbgevent(message, command, silent=False):
        """Add background event
    Example: !addbgevent 60 ping"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        duration = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be duration in seconds", silent)
        if duration is None:
            return
        message.content = bc.config.commands_prefix + ' '.join(command[2:])
        bc.background_events.append(BackgroundEvent(bc.config, message.channel, message, duration))
        await Msg.response(
            message, f"Successfully added background event '{message.content}' with period {duration}", silent)

    @staticmethod
    async def _listbgevent(message, command, silent=False):
        """Print list of background events
    Example: !listbgevent"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, event in enumerate(bc.background_events):
            result += (f"{index}: '{event.message.content}' every {event.period} seconds,"
                       f"channel: <#{event.channel.id}>\n")
        if result:
            await Msg.response(message, result, silent)
        else:
            await Msg.response(message, "No background events found!", silent)
        return result

    @staticmethod
    async def _delbgevent(message, command, silent=False):
        """Delete background event
    Example: !delbgevent 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of background event", silent)
        if index is None:
            return
        if 0 <= index < len(bc.background_events):
            bc.background_events[index].cancel()
            del bc.background_events[index]
            await Msg.response(message, "Successfully deleted background task!", silent)
        else:
            await Msg.response(message, "Invalid index of background task!", silent)

    @staticmethod
    async def _random(message, command, silent=False):
        """Get random number in range [left, right]
    Example: !random 5 10"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        left = await Util.parse_float(
            message, command[1], "Left border should be a number", silent)
        if left is None:
            return
        right = await Util.parse_float(
            message, command[2], "Right border should be a number", silent)
        if right is None:
            return
        if left > right:
            return null(await Msg.response(message, "Left border should be less or equal than right", silent))
        if const.INTEGER_NUMBER.fullmatch(command[1]) and const.INTEGER_NUMBER.fullmatch(command[2]):
            result = str(random.randint(int(left), int(right)))  # integer random
        else:
            result = str(random.uniform(left, right))  # float random
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _randselect(message, command, silent=False):
        """Get random option among provided strings (split by space)
    Example: !randselect a b c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        index = random.randint(1, len(command) - 1)
        result = command[index]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _randselects(message, command, silent=False):
        """Get random option among provided strings (split by semicolon)
    Example: !randselects a;b;c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        options = ' '.join(command[1:]).split(';')
        index = random.randint(0, len(options) - 1)
        result = options[index]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _eqwords(message, command, silent=False):
        """Check if two words are equal or not
    Example: !eqwords a b"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        result = "true" if command[1] == command[2] else "false"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _eqstrs(message, command, silent=False):
        """Check if two strings separated by ';' are equal or not
    Example: !eqstrs a;b"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        options = ' '.join(command[1:]).split(';')
        print(options)
        if len(options) < 2:
            return null(await Msg.response(message, "Too few options to compare", silent))
        if len(options) > 2:
            return null(await Msg.response(message, "Too many options to compare", silent))
        result = "true" if options[0] == options[1] else "false"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _silent(message, command, silent=False):
        """Make the following command silent (without any output to the chat)
    Example: !silent ping"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        command = command[1:]
        if command[0] not in bc.commands.data.keys():
            await Msg.response(message, f"Unknown command '{command[0]}'", silent)
        else:
            cmd = bc.commands.data[command[0]]
            message.content = message.content.split(' ', 1)[-1]
            await cmd.run(message, command, None, silent=True)

    @staticmethod
    async def _time(message, command, silent=False):
        """Show current time
    Examples:
        !time
        !time Europe/Moscow
        !time America/New_York
    Full timezone database list: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        timezone = None
        if len(command) == 2:
            timezone = tz.gettz(command[1])
            if timezone is None:
                return null(
                    await Msg.response(
                        message,
                        "Incorrect timezone. "
                        "Full timezone database list: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>",
                        silent))
        result = str(datetime.datetime.now(timezone)).split('.')[0]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _uptime(message, command, silent=False):
        """Show bot uptime
    Example: !uptime"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.info.uptime
        await Msg.response(message, result, silent)
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
            await Msg.response(message, "Unknown type of activity", silent)

    @staticmethod
    async def _channelid(message, command, silent=False):
        """Get channel ID
    Example: !channelid"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = str(message.channel.id)
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _addalias(message, command, silent=False):
        """Add alias for commands
    Usage: !addalias <command> <alias>
    Example: !addalias ping pong"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        if command[1] not in bc.commands.data.keys():
            return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
        if command[2] in bc.commands.data.keys():
            return null(await Msg.response(message, f"Command '{command[2]}' already exists", silent))
        if command[2] in bc.commands.aliases.keys():
            return null(await Msg.response(message, f"Alias '{command[2]}' already exists", silent))
        bc.commands.aliases[command[2]] = command[1]
        await Msg.response(message, f"Alias '{command[2]}' for '{command[1]}' was successfully created", silent)

    @staticmethod
    async def _delalias(message, command, silent=False):
        """Delete command alias
    Usage: !delalias <alias>
    Example: !delalias pong"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] not in bc.commands.aliases.keys():
            return null(await Msg.response(message, f"Alias '{command[1]}' does not exist", silent))
        bc.commands.aliases.pop(command[1])
        await Msg.response(message, f"Alias '{command[1]}' was successfully deleted", silent)

    @staticmethod
    async def _listalias(message, command, silent=False):
        """Print list of aliases
    Example: !listalias"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        alias_mapping = {}
        for alias, command in bc.commands.aliases.items():
            if command not in alias_mapping.keys():
                alias_mapping[command] = []
            alias_mapping[command].append(alias)
        for command, aliases in alias_mapping.items():
            result += f"{', '.join(aliases)} -> {command}\n"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _img(message, command, silent=False):
        """Send image (use !listimg for list of available images)
    Example: !img <image_name>"""
        if len(command) == 1:
            list_images = os.listdir(const.IMAGES_DIRECTORY)
            if len(list_images) == 0:
                return null(await Msg.response(message, "No images found!", silent))
            result = random.randint(0, len(list_images) - 1)  # integer random
            return null(
                await Msg.response(
                    message, None, silent,
                    files=[discord.File(os.path.join(const.IMAGES_DIRECTORY, list_images[result]))]))
        await _BuiltinInternals.get_image(message, command, silent)

    @staticmethod
    async def _listimg(message, command, silent=False):
        """Print list of available images for !img command
    Example: !listimg"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = []
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                result.append(os.path.splitext(os.path.basename(file))[0])
        result.sort()
        if result:
            await Msg.response(message, "List of available images: [" + ', '.join(result) + "]", silent)
        else:
            await Msg.response(message, "No available images found!", silent)

    @staticmethod
    async def _addimg(message, command, silent=False):
        """Add image for !img command
    Example: !addimg name url"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            return null(await Msg.response(message, f"Incorrect name '{name}'", silent))
        url = command[2]
        ext = url.split('.')[-1]
        if ext not in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
            return null(await Msg.response(message, "Please, provide direct link to image", silent))
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if name == os.path.splitext(os.path.basename(file))[0]:
                    return null(await Msg.response(message, f"Image '{name}' already exists", silent))
        if not os.path.exists(const.IMAGES_DIRECTORY):
            os.makedirs(const.IMAGES_DIRECTORY)
        image_path = os.path.join(const.IMAGES_DIRECTORY, name + '.' + ext)
        with open(image_path, 'wb') as f:
            try:
                hdr = {
                    "User-Agent": "Mozilla/5.0"
                }
                rq = urllib.request.Request(url, headers=hdr)
                with urllib.request.urlopen(rq) as response:
                    f.write(response.read())
            except ValueError:
                return null(await Msg.response(message, "Incorrect image URL format!", silent))
            except Exception as e:
                os.remove(image_path)
                log.error("Image downloading failed!", exc_info=True)
                return null(await Msg.response(message, f"Image downloading failed: {e}", silent))
        if imghdr.what(image_path) is None:
            log.error("Received file is not an image!")
            os.remove(image_path)
            log.info(f"Removed file {image_path}")
            return null(await Msg.response(message, "Received file is not an image", silent))
        await Msg.response(message, f"Image '{name}' successfully added!", silent)

    @staticmethod
    async def _delimg(message, command, silent=False):
        """Delete image for !img command
    Example: !delimg name"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        name = command[1]
        if not re.match(const.FILENAME_REGEX, name):
            return null(await Msg.response(message, f"Incorrect name '{name}'", silent))
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if name == os.path.splitext(os.path.basename(file))[0]:
                    os.remove(os.path.join(const.IMAGES_DIRECTORY, file))
                    return null(await Msg.response(message, f"Successfully removed image '{name}'", silent))
        await Msg.response(message, f"Image '{name}' not found!", silent)

    @staticmethod
    async def _tts(message, command, silent=False):
        """Send text-to-speech (TTS) message
    Example: !tts Hello!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        text = ' '.join(command[1:])
        await Msg.response(message, text, silent, tts=True)
        log.debug(f"Sent TTS message: {text}")

    @staticmethod
    async def _urlencode(message, command, silent=False):
        """Urlencode string
    Example: !urlencode hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[1:])
        result = urllib.request.quote(result.encode("cp1251"))
        await Msg.response(message, result, silent)
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
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _demojify(message, command, silent=False):
        """Demojify text
    Example: !demojify 🇭 🇪 🇱 🇱 🇴"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        text = message.content[len(command[0]) + 1:]
        result = ""
        i = 0
        while i < len(text):
            print(i, text[i])
            if text[i] in emoji.emoji_to_text.keys():
                result += emoji.emoji_to_text[text[i]]
                i += 1
            else:
                result += text[i]
            i += 1
        result = result.strip()
        await Msg.response(message, result, silent)
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
    async def _restart(message, command, silent=False):
        """Restart the bot
    Example: !restart"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        log.info(str(message.author) + " invoked restarting the bot")
        bc.restart_flag = True
        await bc.close()

    @staticmethod
    async def _avatar(message, command, silent=False):
        """Change bot avatar
    Example: !avatar <image>
    Hint: Use !listimg for list of available images"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if os.path.splitext(os.path.basename(file))[0].lower() == command[1].lower():
                    try:
                        with open(os.path.join(const.IMAGES_DIRECTORY, file), "rb") as f:
                            await bc.bot_user.edit(avatar=f.read())
                        await Msg.response(
                            message, f"Successfully changed bot avatar to {command[1]}", silent)
                    except discord.HTTPException as e:
                        await Msg.response(
                            message, f"Failed to change bot avatar.\nError: {e}", silent)
                    return
            else:
                hdr = {
                    "User-Agent": "Mozilla/5.0"
                }
                r = const.EMOJI_REGEX.match(command[1])
                if r is not None:
                    # Discord emoji
                    log.debug(f"Downloading https://cdn.discordapp.com/emojis/{r.group(2)}.png")
                    rq = urllib.request.Request(
                        f"https://cdn.discordapp.com/emojis/{r.group(2)}.png", headers=hdr)
                elif command[1].split('.')[-1] in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
                    # Direct link to an image
                    rq = urllib.request.Request(command[1], headers=hdr)
                else:
                    # Not recognized source
                    break
                os.makedirs(Util.tmp_dir(), exist_ok=True)
                temp_image_file = tempfile.NamedTemporaryFile(dir=Util.tmp_dir())
                try:
                    with urllib.request.urlopen(rq) as response:
                        temp_image_file.write(response.read())
                    with open(temp_image_file.name, "rb") as temp_image_file:
                        await bc.bot_user.edit(avatar=temp_image_file.read())
                except Exception as e:
                    log.error("Image downloading failed!", exc_info=True)
                    return null(await Msg.response(message, f"Image downloading failed: {e}", silent))
                return null(await Msg.response(message, f"Successfully changed bot avatar to {command[1]}", silent))
        min_dist = 100000
        suggestion = ""
        for file in (os.path.splitext(os.path.basename(file))[0].lower() for file in files):
            dist = levenshtein_distance(command[1], file)
            if dist < min_dist:
                suggestion = file
                min_dist = dist
        await Msg.response(
            message,
            f"Image '{command[1]}' is not found! "
            f"Probably you meant '{suggestion}'",
            silent)

    @staticmethod
    async def _message(message, command, silent=False):
        """Get message by its order number (from the end of channel history)
    Example: !message"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        number = await Util.parse_int(
            message, command[1], "Message number should be an integer", silent)
        if number is None:
            return
        if number <= 0:
            await Msg.response(message, "Invalid message number", silent)
            return
        if number > const.MAX_MESSAGE_HISTORY_DEPTH:
            await Msg.response(
                message, f"Message search depth is too big (it can't be more than {const.MAX_MESSAGE_HISTORY_DEPTH})",
                silent)
            return
        result = bc.message_buffer.get(message.channel.id, number)
        if result is not None:
            result = result.content
        else:
            result = await message.channel.history(limit=number + 1).flatten()
            bc.message_buffer.reset(message.channel.id, result)
            result = result[-1].content
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _server(message, command, silent=False):
        """Print information about current server
    Example: !server"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        g = message.guild
        result = (f"**Server**: '{g.name}', members: {g.member_count}, region: {g.region}, "
                  f"created: {g.created_at.replace(microsecond=0)}\n")
        icon_url = f"<{g.icon_url}>" if g.icon_url else "<no icon>"
        result += f"**Icon**: {icon_url}\n"
        text_channels = (f"{ch.name}{' (nsfw)' if ch.nsfw else ''}" for ch in g.text_channels)
        result += f"**Text channels**: {', '.join(text_channels)}\n"
        voice_channels = (f"{ch.name}" for ch in g.voice_channels)
        result += f"**Voice channels**: {', '.join(voice_channels)}\n"
        await Msg.response(message, result, silent)

    @staticmethod
    async def _pin(message, command, silent=False):
        """Print pinned message by its index
    Example: !pin 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Message index should be an integer", silent)
        if index is None:
            return
        pins = await message.channel.pins()
        result = ""
        if 0 <= index < len(pins):
            result = pins[index].content + '\nBy ' + str(message.author)
        else:
            await Msg.response(message, "Invalid index of pinned message!", silent)
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _slowmode(message, command, silent=False):
        """Edit slowmode
    Example: !slowmode 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        duration = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be duration in seconds", silent)
        if duration is None:
            return
        await message.channel.edit(slowmode_delay=duration)
        if duration == 0:
            await Msg.response(message, "Slowmode is disabled for current channel", silent)
        else:
            await Msg.response(message, f"Slowmode is set to {duration} seconds", silent)

    @staticmethod
    async def _curl(message, command, silent=False):
        """Perform HTTP request
    Usage: !curl <url>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        url = command[1]
        r = requests.get(url)
        result = r.text
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _nick(message, command, silent=False):
        """Change nickname
    Usage: !nick walbot"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        new_nick = ' '.join(command[1:])
        await message.guild.me.edit(nick=new_nick)
        await Msg.response(message, f"Bot nickname was changed to '{new_nick}'", silent)

    @staticmethod
    async def _reloadbotcommands(message, command, silent=False):
        """Reload bot commands
    Usage: !reloadbotcommands"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        await Msg.response(message, "Bot commands reloading is started...", silent)
        bc.commands.update(reload=True)
        await Msg.response(message, "Bot commands reloading is finished", silent)

    @staticmethod
    async def _permlevel(message, command, silent=False):
        """Get permission level for user
    Usage: !permlevel
           !permlevel `@user`"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        info = ""
        user_id = 0
        if len(command) == 1:
            info = message.author
            user_id = message.author.id
        elif len(command) == 2:
            if not message.mentions:
                return null(
                    await Msg.response(message, "You need to mention the user "
                                                "for whom you want to get the permission level", silent))
            info = await message.guild.fetch_member(message.mentions[0].id)
            user_id = message.mentions[0].id
        if info is None or user_id not in bc.config.users.keys():
            return null(await Msg.response(message, "Could not get permission level for this user", silent))
        perm_level = bc.config.users[user_id].permission_level
        nick = str(info.nick) + " (" + str(info) + ")" if info.nick is not None else str(info)
        await Msg.response(message, f"Permission level for {nick} is {perm_level}", silent)
