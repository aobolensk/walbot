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

    def _uptime(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime"""
        print(cmd_line)
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.info.uptime
        Command.send_message(execution_ctx, result)
        return result
