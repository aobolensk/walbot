import os
import sys

from .builtin import BuiltinCommands
from .config import bc


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
            for command in self.data:
                command = self.data[command]
                if command.perform is not None:
                    s = "**" + command.name + "**: "
                    s += " \\\n".join(getattr(getattr(sys.modules[command.module_name], command.class_name),
                                              command.perform).__doc__.split('\n'))
                    if command.subcommand:
                        s += " \\\n    *This command can be used as subcommand*"
                    s += '\n'
                    s = s.replace('<', '&lt;').replace('>', '&gt;')
                    result.append(s)
            result = list(set(result))
            result.sort()
            f.write('\n'.join(result))
