"""Time related commands"""

from typing import List, Optional

from dateutil import tz

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Time


class TimeCommands(BaseCmd):
    def bind(self):
        bc.executor.commands["time"] = Command(
            "time", "time", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._time)
        bc.executor.commands["tz"] = Command(
            "time", "tz", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._tz)
        bc.executor.commands["setusertz"] = Command(
            "time", "setusertz", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setusertz)

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
            result = str(Time(timezone).now()).split('.', maxsplit=1)[0]
        else:
            result = str(Time.by_user(execution_ctx).now()).split('.', maxsplit=1)[0]
        await Command.send_message(execution_ctx, result)
        return result

    async def _tz(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get current timezone
    Usage: !tz"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        local_tz = Time().now().astimezone().tzinfo
        await Command.send_message(execution_ctx, f"{local_tz}")

    async def _setusertz(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set timezone for the user
    Usage: !setusertz Europe/Moscow"""
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
        execution_ctx.user.data["tz"] = cmd_line[1] if timezone else None
        local_tz = Time().now().astimezone().tzinfo
        timezone_str = f"{cmd_line[1]}" if timezone else f"default ({local_tz})"
        await Command.send_message(
            execution_ctx,
            f"Set {execution_ctx.message_author()}'s local timezone to {timezone_str}")
