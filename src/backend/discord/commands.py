import importlib
import inspect
import os
from collections import defaultdict
from typing import Any, Dict

from src import const
from src.api.command import BaseCmd
from src.config import Command, bc, log
from src.utils import Util


class Commands:
    def __init__(self) -> None:
        if not hasattr(self, "data"):
            self.data = dict()
        if not hasattr(self, "aliases"):
            self.aliases = dict()
        self.module_help = dict()

    def update(self, reload: bool = False) -> None:
        """Update commands list by loading (reloading) all command modules:
        Public commands: src/*.py
        Private commands: src/private/*.py
        """
        bc.commands = self
        cmd_directory = os.path.join(os.getcwd(), "src", "backend", "discord", "cmd")
        cmd_modules = ['src.backend.discord.cmd.' + os.path.splitext(path)[0] for path in os.listdir(cmd_directory)
                       if os.path.isfile(os.path.join(cmd_directory, path)) and path.endswith(".py")]
        private_cmd_directory = os.path.join(os.getcwd(), "src", "backend", "discord", "cmd", "private")
        cmd_modules += [Util.path_to_module(
            f"src.backend.discord.cmd.private.{os.path.relpath(path, private_cmd_directory)}."
            f"{os.path.splitext(file)[0]}")
            for path, _, files in os.walk(private_cmd_directory) for file in files
            if os.path.isfile(os.path.join(private_cmd_directory, path, file)) and file.endswith(".py")]
        for module in cmd_modules:
            log.debug2(f"Processing commands from module: {module}")
            commands_file = importlib.import_module(module)
            self.module_help[module] = commands_file.__doc__
            if reload:
                importlib.reload(commands_file)
            commands = [obj[1] for obj in inspect.getmembers(commands_file, inspect.isclass)
                        if (obj[1].__module__ == module) and issubclass(obj[1], BaseCmd)]
            if len(commands) == 1:
                commands = commands[0]
                if "bind" in [func[0] for func in inspect.getmembers(commands, inspect.isfunction)
                              if not func[0].startswith('_')]:
                    commands.bind(commands)
                else:
                    log.error(f"Class '{commands.__name__}' does not have bind() function")
            elif len(commands) > 1:
                log.error(f"Module '{module}' have more than 1 class in it")
            else:
                log.error(f"Module '{module}' have no classes in it")
        if not reload:
            self.export_help(const.COMMANDS_DOC_PATH)

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
                        docstring = (
                            command.get_actor().__doc__ or
                            (bc.executor.commands[name].description
                             if name in bc.executor.commands.keys() else None) or
                            "*<No docs provided>*"
                        )
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
                    result[command.module_name].append(s)
                for name in to_remove:
                    del self.data[name]
            result = sorted(result.items())
            # Filling up ToC (table of contents)
            f.write("# Table of Contents:\n")
            for module_name, _ in result:
                if self.module_help[module_name] is not None:
                    module_description = ": " + self.module_help[module_name].strip().split('\n')[0]
                else:
                    module_description = ""
                f.write(
                    "* [Module: " + module_name.split('.')[-1] + "](#module-" + module_name.split('.')[-1] + ")"
                    + module_description + "\n")
            # Add commands grouped by modules
            for module_name, help_list in result:
                f.write("\n# Module: " + module_name.split('.')[-1] + "\n\n" + '\n'.join(sorted(help_list)))

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

    def register_commands(self, module_name: str, class_name: str, commands: Dict[str, Dict[str, Any]]) -> None:
        """Register multiple commands. It calls register_command"""
        for command_name, command_args in commands.items():
            self.register_command(module_name, class_name, command_name, **command_args)
