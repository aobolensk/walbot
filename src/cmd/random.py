import random
from typing import List, Optional

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Util


class RandomCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["random"] = Command(
            "random", "random", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._random)

    async def _random(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get random number in range [left, right]
    Example: !random 5 10"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        left = await Util.parse_float_for_command(
            execution_ctx, cmd_line[1], "Left border should be a number")
        if left is None:
            return
        right = await Util.parse_float_for_command(
            execution_ctx, cmd_line[2], "Right border should be a number")
        if right is None:
            return
        if left > right:
            return Command.send_message(execution_ctx, "Left border should be less or equal than right")
        if const.INTEGER_NUMBER.fullmatch(cmd_line[1]) and const.INTEGER_NUMBER.fullmatch(cmd_line[2]):
            result = str(random.randint(int(left), int(right)))  # integer random
        else:
            result = str(random.uniform(left, right))  # float random
        await Command.send_message(execution_ctx, result)
        return result
