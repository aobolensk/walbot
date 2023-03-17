import functools
from typing import Any, Dict, List

import discord

from src.api.command import CommandBinding, SupportedPlatforms
from src.backend.discord.cmd.builtin import BuiltinCommands
from src.backend.discord.context import DiscordExecutionContext
from src.config import Command, bc, log


class DiscordCommandBinding(CommandBinding):
    def bind(self, cmd_name: str, command: Command):
        if command.module_name is None:
            return
        bc.discord.commands.register_command(
            command.module_name, "DiscordCommandBinding", command.command_name,
            permission=command.permission_level, subcommand=command.subcommand,
            max_execution_time=command.max_execution_time,
        )
        # Add bound commands to CommonCommands class for now
        setattr(
            DiscordCommandBinding, "_" + command.command_name, functools.partial(bind_command, command.command_name))

    def unbind(self, cmd_name: str):
        bc.discord.commands.unregister_command(cmd_name)


class Commands:
    def __init__(self) -> None:
        if not hasattr(self, "data"):
            self.data = dict()
        if not hasattr(self, "aliases"):
            self.aliases = dict()
        self.module_help = dict()

    def update(self, reload: bool = False) -> None:
        bc.discord.commands = self
        # BuiltinCommands class is going to be moved to common commands
        # and finally removed from src/backend/discord/cmd
        builtin_commands = BuiltinCommands()
        builtin_commands.bind()
        binding = DiscordCommandBinding()
        for command in bc.executor.commands.values():
            if command.supported_platforms & SupportedPlatforms.DISCORD:
                binding.bind(command.command_name, command)

    def register_command(self, module_name: str, class_name: str, command_name: str, **kwargs) -> None:
        """Create Command object and save it to commands list"""
        if command_name in self.data.keys() and (
            (hasattr(self.data[command_name], "module_name") and self.data[command_name].module_name == module_name) or
                not hasattr(self.data[command_name], "module_name")):
            return log.debug2(f"Command {module_name} {class_name} {command_name} is already registered")
        log.debug2(f"Registering command: {module_name} {class_name} {command_name}")
        if kwargs.get("message", None):
            self.data[command_name] = Command(module_name, class_name, **kwargs)
        else:
            self.data[command_name] = Command(module_name, class_name, '_' + command_name, **kwargs)
        self.data[command_name].is_global = True
        self.data[command_name].is_private = ".private." in module_name

    def unregister_command(self, command_name: str) -> None:
        self.data.pop(command_name, None)

    def register_commands(self, module_name: str, class_name: str, commands: Dict[str, Dict[str, Any]]) -> None:
        """Register multiple commands. It calls register_command"""
        for command_name, command_args in commands.items():
            self.register_command(module_name, class_name, command_name, **command_args)


async def bind_command(name: str, message: discord.Message, command: List[str], silent: bool = False):
    return await bc.executor.commands[name].run(command, DiscordExecutionContext(message, silent))
