from typing import List

from src import const
from src.api.command import BaseCmd, Command, ExecutionContext, Implementation
from src.config import bc
from src.utils import Util


class BuiltinCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["ping"] = Command(
            "builtin", "ping", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="Pong!")
        bc.executor.commands["uptime"] = Command(
            "builtin", "uptime", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._uptime)
        bc.executor.commands["about"] = Command(
            "builtin", "about", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._about)
        bc.executor.commands["version"] = Command(
            "builtin", "version", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._version)
        bc.executor.commands["curl"] = Command(
            "builtin", "curl", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._curl)

    def _uptime(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime
    Example: !uptime"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.info.uptime
        Command.send_message(execution_ctx, result)
        return result

    def _about(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get information about the bot
    Examples:
        !about
        !about -v   <- verbose
        !about -vv  <- even more verbose
"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if not hasattr(bc, "discord_bot_user"):
            return Command.send_message(execution_ctx, "Bot is not loaded yet!")
        verbosity = 0
        if len(cmd_line) > 1:
            if cmd_line[1] == '-v':
                verbosity = 1
            elif cmd_line[1] == '-vv':
                verbosity = 2
            else:
                return Command.send_message(
                    execution_ctx, f"Unknown argument '{cmd_line[1]}' for '{cmd_line[0]}' command")
        result = bc.info.get_full_info(verbosity)
        Command.send_message(execution_ctx, result)

    def _version(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get version of the bot
    Examples:
        !version
        !version short"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        result = bc.info.version
        if len(cmd_line) == 2 and (cmd_line[1] == 's' or cmd_line[1] == 'short'):
            result = result[:7]
        Command.send_message(execution_ctx, result)
        return result

    def _curl(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Perform HTTP request
    Usage:
        !curl <url>
        !curl <url> --no-proxy
    """
        if not Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        url = cmd_line[1]
        use_proxy = True if len(cmd_line) == 3 and cmd_line[2] == "--no-proxy" else False
        try:
            r = Util.request(url, use_proxy=use_proxy)
            result = r.get_text()
            Command.send_message(execution_ctx, result)
            return result
        except Exception as e:
            Command.send_message(execution_ctx, f"Request failed: {e}")
