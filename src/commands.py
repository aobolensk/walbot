import inspect
import os

from .config import Command
from .config import bc
from .config import log


class Commands:
    def __init__(self, config):
        self.config = config
        if not hasattr(self, "data"):
            self.data = dict()
        if not hasattr(self, "aliases"):
            self.aliases = dict()

    def update(self):
        bc.commands = self
        cmd_directory = os.path.join(os.path.dirname(__file__), "cmd")
        cmd_modules = ['.' + os.path.splitext(path)[0] for path in os.listdir(cmd_directory)
                       if os.path.isfile(os.path.join(cmd_directory, path)) and path.endswith(".py")]
        for module in cmd_modules:
            builtin = __import__("src.cmd" + module, fromlist=['object'])
            commands = [obj[1] for obj in inspect.getmembers(builtin, inspect.isclass)
                        if obj[1].__module__ == "src.cmd" + module]
            if len(commands) == 1:
                commands = commands[0]
                if "bind" in [func[0] for func in inspect.getmembers(commands, inspect.isfunction)
                              if not func[0].startswith('_')]:
                    commands.bind(commands)
                else:
                    log.error("Class '{}' does not have bind() function".format(commands.__name__))
            elif len(commands) >= 1:
                log.error("Module 'src.cmd{}' have more than 1 class in it".format(module))
            else:
                log.error("Module 'src.cmd{}' have no classes in it".format(module))
        self.export_help()

    def export_help(self):
        with open(os.path.join(os.getcwd(), "docs", "Help.md"), "w", encoding="utf-8", newline='\n') as f:
            result = []
            repeat = True
            while repeat:
                repeat = False
                for name, command in self.data.items():
                    if command.perform is not None:
                        s = "**" + name + "**: "
                        try:
                            s += " \\\n".join(command.get_actor().__doc__.split('\n'))
                        except AttributeError:
                            del self.data[name]
                            log.warning("Command '{}' is not found and deleted from config and documentation".format(
                                        name))
                            repeat = True
                            break
                        if command.subcommand:
                            s += " \\\n    *This command can be used as subcommand*"
                        s += '\n'
                        s = s.replace('<', '&lt;').replace('>', '&gt;')
                        result.append(s)
            f.write('\n'.join(sorted(list(set(result)))))

    def register_command(self, module_name, class_name, command_name, **kwargs):
        if command_name not in self.data.keys():
            if kwargs.get("message", None):
                self.data[command_name] = Command(module_name, class_name, **kwargs)
            else:
                self.data[command_name] = Command(module_name, class_name, '_' + command_name, **kwargs)
            self.data[command_name].is_global = True
