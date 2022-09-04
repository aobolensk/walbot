import datetime
import subprocess
import sys
from typing import List, Optional

from dateutil import tz

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.utils import Util


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
        bc.executor.commands["uptime"] = Command(
            "builtin", "uptime", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._uptime)
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
        bc.executor.commands["time"] = Command(
            "builtin", "time", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._time)
        bc.executor.commands["extexec"] = Command(
            "builtin", "extexec", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=True, impl_func=self._extexec)
        bc.executor.commands["curl"] = Command(
            "builtin", "curl", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._curl)
        bc.executor.commands["wme"] = Command(
            "builtin", "wme", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._wme)
        bc.executor.commands["donotupdatestate"] = Command(
            "builtin", "donotupdatestate", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._donotupdatestate)
        bc.executor.commands["getmentioncmd"] = Command(
            "builtin", "getmentioncmd", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=True, impl_func=self._getmentioncmd)
        bc.executor.commands["setmentioncmd"] = Command(
            "builtin", "setmentioncmd", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setmentioncmd)

    async def _uptime(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime
    Example: !uptime"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.info.uptime
        await Command.send_message(execution_ctx, result)
        return result

    async def _about(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get information about the bot
    Examples:
        !about
        !about -v   <- verbose
        !about -vv  <- even more verbose
"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        verbosity = 0
        if len(cmd_line) > 1:
            if cmd_line[1] == '-v':
                verbosity = 1
            elif cmd_line[1] == '-vv':
                verbosity = 2
            else:
                return await Command.send_message(
                    execution_ctx, f"Unknown argument '{cmd_line[1]}' for '{cmd_line[0]}' command")
        result = bc.info.get_full_info(verbosity)
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

    async def _time(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Show current time
    Examples:
        !time
        !time Europe/Moscow
        !time America/New_York
    Full timezone database list: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        timezone = None
        if len(cmd_line) == 2:
            timezone = tz.gettz(cmd_line[1])
            if timezone is None:
                return await Command.send_message(
                    execution_ctx,
                    "Incorrect timezone. "
                    "Full timezone database list: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>")
        result = str(datetime.datetime.now(timezone)).split('.', maxsplit=1)[0]
        await Command.send_message(execution_ctx, result)
        return result

    async def _extexec(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Execute external shell command
    Note: Be careful when you are executing external commands!
    Example: !extexec uname -a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        print(' '.join(cmd_line[1:]))
        return await Util.run_external_command(execution_ctx, ' '.join(cmd_line[1:]))

    async def _curl(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Perform HTTP request
    Usage:
        !curl <url>
        !curl <url> --no-proxy
    """
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        url = cmd_line[1]
        use_proxy = True if len(cmd_line) == 3 and cmd_line[2] == "--no-proxy" else False
        try:
            r = Util.request(url, use_proxy=use_proxy)
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

    async def _donotupdatestate(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print current state of "Do Not Update" flag which blocks automatic bot updates
    Usage: !donotupdatestate"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = ""
        if bc.do_not_update[DoNotUpdateFlag.VOICE]:
            result += "❌ Bot is connected to voice channel\n"
        else:
            result += "✅ Bot is not connected to voice channel\n"
        if bc.do_not_update[DoNotUpdateFlag.DISCORD_REMINDER] or bc.do_not_update[DoNotUpdateFlag.TELEGRAM_REMINDER]:
            result += "❌ Next reminder will be sent very soon\n"
        else:
            result += "✅ No reminders in next several minutes\n"
        if bc.do_not_update[DoNotUpdateFlag.POLL]:
            result += f"❌ {bc.do_not_update[DoNotUpdateFlag.POLL]} polls are active\n"
        else:
            result += "✅ No polls are active\n"
        if bc.do_not_update[DoNotUpdateFlag.TIMER]:
            result += f"❌ {bc.do_not_update[DoNotUpdateFlag.TIMER]} timers are active\n"
        else:
            result += "✅ No timers are active\n"
        if bc.do_not_update[DoNotUpdateFlag.STOPWATCH]:
            result += f"❌ {bc.do_not_update[DoNotUpdateFlag.STOPWATCH]} stopwatches are active\n"
        else:
            result += "✅ No stopwatches are active\n"
        await Command.send_message(execution_ctx, result)

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
