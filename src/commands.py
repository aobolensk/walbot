import importlib
import inspect
import os

from src import const
from src.config import Command, bc, log


class BaseCmd:
    @classmethod
    def get_classname(cls):
        return cls.__name__

    def bind(self):
        raise NotImplementedError(f"Class {self.get_classname()} does not have bind() function")


class Commands:
    def __init__(self):
        if not hasattr(self, "data"):
            self.data = dict()
        if not hasattr(self, "aliases"):
            self.aliases = dict()

    def _path_to_module(self, path: str):
        result = ''
        for c in path:
            if c != os.pathsep and c != '.' or result[-1] != '.':
                result += c
        return result

    def update(self, reload=False):
        bc.commands = self
        cmd_directory = os.path.join(os.path.dirname(__file__), "cmd")
        cmd_modules = ['src.cmd.' + os.path.splitext(path)[0] for path in os.listdir(cmd_directory)
                       if os.path.isfile(os.path.join(cmd_directory, path)) and path.endswith(".py")]
        private_cmd_directory = os.path.join(os.path.dirname(__file__), "cmd", "private")
        cmd_modules += [self._path_to_module(
            f"src.cmd.private.{os.path.relpath(path, private_cmd_directory)}."
            f"{os.path.splitext(file)[0]}")
            for path, _, files in os.walk(private_cmd_directory) for file in files
            if os.path.isfile(os.path.join(private_cmd_directory, path, file)) and file.endswith(".py")]
        for module in cmd_modules:
            log.debug2(f"Processing commands from module: {module}")
            commands_file = importlib.import_module(module)
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

    def export_help(self, file_path):
        with open(file_path, "w", encoding="utf-8", newline='\n') as f:
            f.write(
                "<!-- WARNING! This file is automatically generated, do not change it manually -->\n"
                "<!-- To regenerate this file launch `python walbot.py docs` command or simply launch the bot -->\n"
                "\n"
            )
            repeat = True
            while repeat:
                result = []
                repeat = False
                to_remove = []
                for name, command in self.data.items():
                    if command.perform is None or command.is_private:
                        continue
                    s = "**" + name + "**: "
                    try:
                        s += " \\\n".join(command.get_actor().__doc__.split('\n'))
                    except (AttributeError, KeyError):
                        to_remove.append(name)
                        log.warning(f"Command '{name}' is not found and removed from config and documentation")
                        repeat = True
                        continue
                    if command.subcommand:
                        s += " \\\n    *This command can be used as subcommand*"
                    s += '\n'
                    s = s.replace('<', '&lt;').replace('>', '&gt;')
                    result.append(s)
                for name in to_remove:
                    del self.data[name]
            f.write('\n'.join(sorted(result)))

    def register_command(self, module_name, class_name, command_name, **kwargs):
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
