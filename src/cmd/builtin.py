import math
import subprocess
import sys
from typing import List, Optional

import discord
import telegram

from src import const
from src.api.command import (
    BaseCmd,
    Command,
    Implementation,
    SupportedPlatforms
)
from src.api.execution_context import ExecutionContext
from src.backend.discord.embed import DiscordEmbed
from src.cmdarg_parser import CmdArgParser
from src.config import bc
from src.message_cache import CachedMsg
from src.shell import Shell
from src.utils import Util


class _BuiltinInternals:
    async def discord_profile(cmd_line: List[str], execution_ctx: ExecutionContext, user: discord.Member) -> None:
        roles = ', '.join([x if x != const.ROLE_EVERYONE else const.ROLE_EVERYONE[1:] for x in map(str, user.roles)])
        nick = f'{user.nick} ({user})' if user.nick is not None else f'{user}'
        title = nick + (' (bot)' if user.bot else '')
        flags = ' '.join([str(flag[0]) for flag in user.public_flags if flag[1]])
        e = DiscordEmbed()
        e.title(title)
        if user.avatar:
            e.thumbnail(str(user.avatar))
        e.add_field("Created at", str(user.created_at).split('.', maxsplit=1)[0], True)
        e.add_field("Joined this server at", str(user.joined_at).split('.', maxsplit=1)[0], True)
        e.add_field("Roles", roles, True)
        if len(cmd_line) == 1:
            # If user requests their own profile, show their status
            # otherwise it is not available
            e.add_field("Status",
                        f"desktop: {user.desktop_status}\n"
                        f"mobile: {user.mobile_status}\n"
                        f"web: {user.web_status}", True)
        e.add_field(
            "Permission level",
            bc.config.discord.users[user.id].permission_level if user.id in bc.config.discord.users.keys() else 0, True)
        e.add_field("User timezone", bc.config.discord.users[user.id].data["tz"], True)
        if flags:
            e.add_field("Flags", flags)
        await Command.send_message(execution_ctx, None, embed=e.get())

    async def telegram_profile(cmd_line: List[str], execution_ctx: ExecutionContext, user: telegram.User) -> None:
        result = f"{execution_ctx.message_author()} profile\n"
        result += f"Permission level: {bc.config.telegram.users[user.id].permission_level}"
        await Command.send_message(execution_ctx, result)


class BuiltinCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["ping"] = Command(
            "builtin", "ping", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="🏓 Pong! @author@ 🏓")
        bc.executor.commands["echo"] = Command(
            "builtin", "echo", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="@args@")
        bc.executor.commands["code"] = Command(
            "builtin", "code", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="`@args@`",
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["codeblock"] = Command(
            "builtin", "codeblock", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="```\n@args@\n```",
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["uptime"] = Command(
            "builtin", "uptime", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._uptime)
        bc.executor.commands["help"] = Command(
            "builtin", "help", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._help)
        bc.executor.commands["about"] = Command(
            "builtin", "about", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._about)
        bc.executor.commands["shutdown"] = Command(
            "builtin", "shutdown", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._shutdown)
        bc.executor.commands["restart"] = Command(
            "builtin", "restart", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._restart)
        bc.executor.commands["version"] = Command(
            "builtin", "version", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._version)
        bc.executor.commands["extexec"] = Command(
            "builtin", "extexec", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=True, impl_func=self._extexec)
        bc.executor.commands["curl"] = Command(
            "builtin", "curl", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._curl)
        bc.executor.commands["wme"] = Command(
            "builtin", "wme", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._wme)
        bc.executor.commands["getmentioncmd"] = Command(
            "builtin", "getmentioncmd", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=True, impl_func=self._getmentioncmd)
        bc.executor.commands["setmentioncmd"] = Command(
            "builtin", "setmentioncmd", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setmentioncmd)
        bc.executor.commands["profile"] = Command(
            "builtin", "profile", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._profile,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["server"] = Command(
            "builtin", "server", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._server,
            supported_platforms=(SupportedPlatforms.DISCORD))
        bc.executor.commands["message"] = Command(
            "builtin", "message", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._message)
        bc.executor.commands["tts"] = Command(
            "builtin", "tts", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._tts,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["status"] = Command(
            "builtin", "status", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._status,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["nick"] = Command(
            "builtin", "nick", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._nick,
            supported_platforms=SupportedPlatforms.DISCORD)

    async def _uptime(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime
    Example: !uptime"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.info.uptime
        await Command.send_message(execution_ctx, result)
        return result

    async def _help(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of commands and get examples
    Usage:
        !help
        !help -p (alternative: !help --plain)
        !help -a (alternative: !help --all)
        !help <command_name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1):
            return
        parser = CmdArgParser(execution_ctx)
        parser.add_argument("command_name", action="store", default=None, nargs='?')
        parser.add_argument("-p", "--plain", action="store_true", default=False)
        parser.add_argument("-a", "--all", action="store_true", default=False)
        args = parser.parse_args(cmd_line)
        if args is None:
            return

        def get_help_for_command(cmd_name: str) -> str:
            if cmd_name not in bc.executor.commands.keys():
                result = f"Unknown command '{cmd_name}'"
                return
            cmd = bc.executor.commands[cmd_name]
            result = ""
            if cmd.impl_type == Implementation.FUNCTION:
                result += cmd.description
            elif cmd.impl_type == Implementation.MESSAGE:
                result += cmd.impl_message
            elif cmd.impl_type == Implementation.EXTERNAL_CMDLINE:
                result += "calls external command `" + cmd.impl_message + "`"
            return result

        if args.command_name is not None:
            # !help <command_name>
            result = get_help_for_command(args.command_name)
            await Command.send_message(execution_ctx, result)
            return
        # !help
        version = bc.info.version
        result = "Help:\n"
        commands = sorted([
            (cmd_name, get_help_for_command(cmd_name))
            for cmd_name, cmd in bc.executor.commands.items()
            if args.all or cmd.impl_type != Implementation.FUNCTION or cmd.module_name.startswith("plugin_")])
        if execution_ctx.platform == const.BotBackend.DISCORD:
            commands.insert(
                0, ("Built-in commands", (
                    f"<{const.GIT_REPO_LINK}/blob/" +
                    (version if version != ' ' else "master") + "/" + const.DISCORD_COMMANDS_DOC_PATH + ">")))
        elif execution_ctx.platform == const.BotBackend.DISCORD:
            commands.insert(
                0, ("Built-in commands", (
                    f"<{const.GIT_REPO_LINK}/blob/" +
                    (version if version != ' ' else "master") + "/" + const.TELEGRAM_COMMANDS_DOC_PATH + ">")))

        if execution_ctx.platform == const.BotBackend.DISCORD and not args.plain:
            cur_list = 1
            total_list = int(math.ceil(len(commands) / const.DISCORD_MAX_EMBED_FILEDS_COUNT))
            for chunk in Util.split_by_chunks(commands, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
                title = "Help"
                if total_list > 1:
                    title += f" ({cur_list}/{total_list})"
                cur_list += 1
                embed = discord.Embed(title=title, color=0x717171)
                for cmd_name, cmd_desc in chunk:
                    cmd_desc = Util.cut_string(cmd_desc, 1024)
                    embed.add_field(name=cmd_name, value=cmd_desc, inline=False)
                await Command.send_message(execution_ctx, None, embed=embed)
            return
        else:
            for cmd_name, cmd_desc in commands:
                result += f"{cmd_name}: {cmd_desc}\n"

        await Command.send_message(execution_ctx, result, suppress_emdebs=True)

    async def _about(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get information about the bot
    Examples:
        !about
        !about -v   <- verbose
        !about -vv  <- even more verbose
"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        parser = CmdArgParser(execution_ctx)
        parser.add_argument("-v", "--verbose", action="store_const", dest="verbosity", const=1, default=0)
        parser.add_argument(
            "-vv", "--verbose2", "--very-verbose", action="store_const", dest="verbosity", const=2, default=0)
        args = parser.parse_args(cmd_line)
        if args is None:
            return
        result = bc.info.get_full_info(args.verbosity)
        await Command.send_message(execution_ctx, result, suppress_embeds=True)

    async def _shutdown(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Shutdown the bot
    Example: !shutdown"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        await Command.send_message(execution_ctx, f"{execution_ctx.message_author()} invoked bot shutdown!")
        subprocess.call([sys.executable, "walbot.py", "stop"])

    async def _restart(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Restart the bot
    Example: !restart"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        await Command.send_message(execution_ctx, f"{execution_ctx.message_author()} invoked restarting the bot!")
        subprocess.call([sys.executable, "walbot.py", "restart"])

    async def _version(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        result = bc.info.version
        if len(cmd_line) == 2 and (cmd_line[1] == 's' or cmd_line[1] == 'short'):
            result = result[:7]
        await Command.send_message(execution_ctx, result)
        return result

    async def _extexec(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Execute external shell command
    Note: Be careful when you are executing external commands!
    Example: !extexec uname -a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        return await Shell.run_and_send_stdout(execution_ctx, ' '.join(cmd_line[1:]))

    async def _curl(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Perform HTTP request
    Usage:
        !curl <url>
        !curl <url> --no-proxy
    """
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        parser = CmdArgParser(execution_ctx)
        parser.add_argument("url")
        parser.add_argument("--no-proxy", action="store_false", dest="use_proxy")
        args = parser.parse_args(cmd_line)
        if args is None:
            return
        try:
            r = Util.request(args.url, use_proxy=args.use_proxy)
            result = r.get_text()
            await Command.send_message(execution_ctx, result)
            return result
        except Exception as e:
            await Command.send_message(execution_ctx, f"Request failed: {e}")

    async def _wme(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Send direct message to author with something
    Example: !wme Hello!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[1:])
        if not result:
            return
        result = "You asked me to send you this: " + result
        await execution_ctx.send_direct_message(execution_ctx.message_author_id(), result)

    async def _getmentioncmd(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get current command which is executed on bot ping
    Example: !getmentioncmd"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        await Command.send_message(execution_ctx, bc.config.on_mention_command)

    async def _setmentioncmd(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set current command which is executed on bot ping
    Examples:
        !setmentioncmd ping
        !setmentioncmd markov"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        command = ' '.join(cmd_line[1:])
        bc.config.on_mention_command = command
        await Command.send_message(execution_ctx, f"Command '{command}' was set on bot mention")

    async def _profile(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print information about user
    Examples:
        !profile
        !profile `@user`"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        user = ""
        if execution_ctx.platform == const.BotBackend.DISCORD:
            if len(cmd_line) == 1:
                user = execution_ctx.message.author
            elif len(cmd_line) == 2:
                if not execution_ctx.message.mentions:
                    return await Command.send_message(
                        execution_ctx, "You need to mention the user you want to get profile of")
                user = await execution_ctx.message.guild.fetch_member(execution_ctx.message.mentions[0].id)
            if user is None:
                return await Command.send_message(execution_ctx, "Could not get information about this user")
            await _BuiltinInternals.discord_profile(cmd_line, execution_ctx, user)
        elif execution_ctx.platform == const.BotBackend.TELEGRAM:
            if len(cmd_line) == 1:
                user = execution_ctx.update.message.from_user
            elif len(cmd_line) == 2:
                return await Command.send_message(
                    execution_ctx, "Getting others profile is not supported on Telegram backend")
            await _BuiltinInternals.telegram_profile(cmd_line, execution_ctx, user)
        else:
            await Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    async def _server(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print information about current server
    Example: !server"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if execution_ctx.platform == const.BotBackend.DISCORD:
            g = execution_ctx.message.guild
            e = DiscordEmbed()
            e.title(g.name)
            if g.icon:
                e.thumbnail(str(g.icon))
            e.add_field("Members", str(g.member_count), True)
            e.add_field("Created", str(g.created_at.replace(microsecond=0)), True)
            if g.owner is not None:
                e.add_field("Owner", str(g.owner).split('#', 1)[0], True)
            e.add_field("Text channels",
                        ', '.join([f"{ch.name}{' (nsfw)' if ch.nsfw else ''}" for ch in g.text_channels]), True)
            e.add_field("Voice channels", ', '.join([f"{ch.name}" for ch in g.voice_channels]), True)
            e.add_field("Server emojis", ' '.join([str(emoji) for emoji in g.emojis]))
            e.add_field("Verification level", str(g.verification_level), True)
            e.add_field("Server Boost level", str(g.premium_tier), True)
            await Command.send_message(execution_ctx, None, embed=e.get())
        else:
            await Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    async def _message(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get message by its order number counting from the newest message
    Example: !message"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        number = await Util.parse_int(
            execution_ctx, cmd_line[1], "Message number should be an integer")
        if number is None:
            return
        if number <= 0:
            await Command.send_message(execution_ctx, "Invalid message number")
        if number > const.MAX_MESSAGE_HISTORY_DEPTH:
            return await Command.send_message(
                execution_ctx,
                f"Message search depth is too big (it can't be more than {const.MAX_MESSAGE_HISTORY_DEPTH})")
        result = bc.message_cache.get(execution_ctx.channel_id(), number)
        if result is None:
            if execution_ctx.platform == const.BotBackend.DISCORD:
                result = await execution_ctx.message.channel.history(limit=number + 1).flatten()
                history_data = [CachedMsg(msg.content, str(msg.author.id)) for msg in result]
                bc.message_cache.reset(execution_ctx.channel_id(), history_data)
                result = history_data[-1]
            else:
                return await Command.send_message(execution_ctx, "Message index is too big")
        result = result.message
        await Command.send_message(execution_ctx, result)
        return result

    async def _tts(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Send text-to-speech (TTS) message
    Example: !tts Hello!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        text = ' '.join(cmd_line[1:])
        await Command.send_message(execution_ctx, text, tts=True)

    async def _status(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Change bot status
    Examples:
        !status idle
        !status playing Dota 2
    Possible activities: [playing, streaming, watching, listening]
    Possible bot statuses: [online, idle, dnd, invisible]"""
        if len(cmd_line) == 1:
            await bc.discord.change_status("", discord.ActivityType.playing)
        elif cmd_line[1] == "playing":
            await bc.discord.change_status(' '.join(cmd_line[2:]), discord.ActivityType.playing)
        elif cmd_line[1] == "streaming":
            await bc.discord.change_status(' '.join(cmd_line[2:]), discord.ActivityType.streaming)
        elif cmd_line[1] == "watching":
            await bc.discord.change_status(' '.join(cmd_line[2:]), discord.ActivityType.watching)
        elif cmd_line[1] == "listening":
            await bc.discord.change_status(' '.join(cmd_line[2:]), discord.ActivityType.listening)
        elif cmd_line[1] == "online":
            await bc.discord.change_presence(status=discord.Status.online)
        elif cmd_line[1] == "idle":
            await bc.discord.change_presence(status=discord.Status.idle)
        elif cmd_line[1] == "dnd":
            await bc.discord.change_presence(status=discord.Status.dnd)
        elif cmd_line[1] == "invisible":
            await bc.discord.change_presence(status=discord.Status.invisible)
        else:
            await Command.send_message(execution_ctx, "Unknown type of activity")

    async def _nick(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Change nickname
    Usage: !nick walbot"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        new_nick = ' '.join(cmd_line[1:])
        try:
            await execution_ctx.message.guild.me.edit(nick=new_nick)
        except discord.HTTPException as e:
            await Command.send_message(execution_ctx, f"Bot nickname change failed. ERROR: '{e}'")
            return
        await Command.send_message(execution_ctx, f"Bot nickname was changed to '{new_nick}'")
