"""Math operations"""

import functools

from src import const
from src.backend.discord.commands import bind_command
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
from src.utils import Util, null


class MathCommands(BaseCmd):
    def bind(self):
        bc.discord.commands.register_commands(__name__, self.get_classname(), {
            "calc": dict(permission=const.Permission.USER.value, subcommand=True),
            "if": dict(permission=const.Permission.USER.value, subcommand=True),
        })

        self._calc = functools.partial(bind_command, "calc")

    @staticmethod
    async def _if(message, command, silent=False):
        """If expression is true (!= 0) then return first expression otherwise return the second one
    Examples:
        !if 1 It's true;It's false -> It's true
        !if 0 It's true;It's false -> It's false
"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        condition = command[1]

        true = ["true"]
        false = ["false"]

        if condition.lower() not in true + false:
            condition = await Util.parse_int(
                message, command[1], f"Second parameter should be either number or {', '.join(true + false)}", silent)
            if condition is None:
                return
        else:
            # Handle keywords that can be used in conditions
            if condition.lower() in true:
                condition = 1
            elif condition.lower() in false:
                condition = 0

        expressions = ' '.join(command[2:]).split(';')
        if len(expressions) != 2:
            return null(
                await Msg.response(
                    message, f"There should be only 2 branches ('then' and 'else') "
                             f"separated by ';' in '{command[0]}' command", silent))
        result = expressions[0] if condition != 0 else expressions[1]
        await Msg.response(message, result, silent)
        return result
