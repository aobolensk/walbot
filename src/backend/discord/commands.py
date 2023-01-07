import functools
from collections import defaultdict
from typing import Any, Dict, List

import discord

from src import const
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
        if not reload:
            self.export_help(const.DISCORD_COMMANDS_DOC_PATH)  # Discord legacy help export

    def export_help(self, file_path: str) -> None:
        """Generate and export help for loaded commands to md file in docs directory"""
        with open(file_path, "w", encoding="utf-8", newline='\n') as f:
            f.write(
                "<!-- WARNING! This file is automatically generated, do not change it manually -->\n"
                "<!-- To regenerate this file launch `python walbot.py docs` command or simply launch the bot -->\n"
                "\n"
            )
            repeat = True
            while repeat:
                result = defaultdict(list)
                repeat = False
                to_remove = []
                for name, command in self.data.items():
                    if command.perform is None or command.is_private:
                        continue
                    s = "**" + name + "**: "
                    try:
                        docstring = "*<No docs provided>*"
                        if (command.get_actor().__doc__ and
                                "new function with partial application" not in command.get_actor().__doc__):
                            docstring = command.get_actor().__doc__
                        elif name in bc.executor.commands.keys():
                            docstring = bc.executor.commands[name].description
                        s += " \\\n".join(docstring.strip().split('\n'))
                    except (AttributeError, KeyError):
                        to_remove.append(name)
                        log.warning(f"Command '{name}' is not found and removed from config and documentation")
                        repeat = True
                        continue
                    if command.subcommand:
                        s += " \\\n    *This command can be used as subcommand*"
                    s += '\n'
                    s = s.replace('<', '&lt;').replace('>', '&gt;')
                    result[command.module_name.split('.')[-1]].append(s)
                for name in to_remove:
                    del self.data[name]
            result = sorted(result.items())
            # Filling up ToC (table of contents)
            f.write("# Table of Contents:\n")
            for module_name, _ in result:
                f.write("* [Module: " + module_name + "](#module-" + module_name + ")\n")
            # Add commands grouped by modules
            for module_name, help_list in result:
                f.write("\n# Module: " + module_name + "\n\n" + '\n'.join(sorted(help_list)))

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
