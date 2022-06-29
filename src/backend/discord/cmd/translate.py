from urllib.parse import urlparse

from googletrans import Translator
from httpcore import SyncHTTPProxy

from src import const
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
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
        proxy = dict()
        if Util.proxy.http():
            http_parse_res = urlparse(Util.proxy.http())
            proxy["http"] = SyncHTTPProxy((
                http_parse_res.scheme.encode("utf-8"), http_parse_res.hostname.encode("utf-8"),
                int(http_parse_res.port)))
        if Util.proxy.https():
            https_parse_res = urlparse(Util.proxy.https())
            proxy["https"] = SyncHTTPProxy((
                https_parse_res.scheme.encode("utf-8"), https_parse_res.hostname.encode("utf-8"),
                int(https_parse_res.port)))
        translator = Translator(proxies=proxy)
        dst_language = command[1]
        text = " ".join(command[2:])
        try:
            translation = translator.translate(text, dest=dst_language)
            await Msg.response(message, translation.text, silent)
            return translation.text
        except Exception as e:
            await Msg.response(message, f"ERROR! Could not translate text: {e}", silent)
