from googletrans import Translator

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.backend.discord.message import Msg
from src.utils import Util


class TranslateCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "translate": dict(permission=const.Permission.USER.value, subcommand=True),
        })

    @staticmethod
    async def _translate(message, command, silent=False):
        """Translate text to specified language
    Usage: !translate <lang> <text>"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        translator = Translator()
        dst_language = command[1]
        text = " ".join(command[2:])
        translation = translator.translate(text, dest=dst_language)
        await Msg.response(message, translation.text, silent)
