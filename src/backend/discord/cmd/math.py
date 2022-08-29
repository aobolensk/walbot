"""Math operations"""

import functools

from src import const
from src.backend.discord.commands import bind_command
from src.commands import BaseCmd
from src.config import bc


class MathCommands(BaseCmd):
    def bind(self):
        bc.discord.commands.register_commands(__name__, self.get_classname(), {
            "calc": dict(permission=const.Permission.USER.value, subcommand=True),
            "if": dict(permission=const.Permission.USER.value, subcommand=True),
        })

        self._calc = functools.partial(bind_command, "calc")
        self._if = functools.partial(bind_command, "if")
