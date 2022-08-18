from typing import List

from src import const
from src.api.command import BaseCmd, Command, ExecutionContext, Implementation
from src.config import bc


class BuiltinCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self, commands) -> None:
        commands["ping"] = Command(
            "builtin", "ping", const.Permission.USER, Implementation.MESSAGE,
            subcommand=True, impl_message="Pong!")
        commands["uptime"] = Command(
            "builtin", "uptime", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._uptime)
        commands["about"] = Command(
            "builtin", "about", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._about)
        commands["version"] = Command(
            "builtin", "version", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._version)

    def _uptime(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime"""
        print(cmd_line)
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.info.uptime
        Command.send_message(execution_ctx, result)
        return result

    def _about(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get information about the bot"""
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
        """Get bot version"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        result = bc.info.version
        if len(cmd_line) == 2 and (cmd_line[1] == 's' or cmd_line[1] == 'short'):
            result = result[:7]
        Command.send_message(execution_ctx, result)
        return result
