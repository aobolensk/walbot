import os

from . import const
from .config import Command
from .config import log
from .config import bc

from .builtin import BuiltinCommands


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
                    s += " \\\n".join(command.perform.__doc__.split('\n'))
                    if command.subcommand:
                        s += " \\\n    *This command can be used as subcommand*"
                    s += '\n'
                    s = s.replace('<', '&lt;').replace('>', '&gt;')
                    result.append(s)
            result = list(set(result))
            result.sort()
            f.write('\n'.join(result))

    async def response(self, message, content, silent, **kwargs):
        if not silent:
            if content:
                for chunk in Command.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    await message.channel.send(chunk, tts=kwargs.get("tts", False))
            if kwargs.get("embed", None):
                await message.channel.send(embed=kwargs["embed"], tts=kwargs.get("tts", False))
        else:
            log.info("[SILENT] -> " + content)
