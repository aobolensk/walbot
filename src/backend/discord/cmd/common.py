import functools

from src.api.command import SupportedPlatforms
from src.backend.discord.commands import bind_command
from src.commands import BaseCmd
from src.config import bc


class CommonCommands(BaseCmd):
    def bind(self):
        for command in bc.executor.commands.values():
            if command.supported_platforms & SupportedPlatforms.DISCORD:
                if command.module_name is None:
                    continue
                bc.discord.commands.register_command(
                    command.module_name, self.get_classname(), command.command_name,
                    permission=command.permission_level, subcommand=command.subcommand,
                )
                setattr(self, "_" + command.command_name, functools.partial(bind_command, command.command_name))
