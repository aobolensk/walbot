import os
import sys

from .builtin import BuiltinCommands
from .config import bc
from .config import log


class Commands:
    def __init__(self, config):
        self.config = config
        self.data = dict()
        if not hasattr(self, "aliases"):
            self.aliases = dict()
        self.update()

    def update(self):
        bc.commands = self
        BuiltinCommands().bind()
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
                            s += " \\\n".join(getattr(getattr(sys.modules[command.module_name], command.class_name),
                                                      command.perform).__doc__.split('\n'))
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
