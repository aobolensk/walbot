"""Commands that get data from online services"""

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.backend.discord.message import Msg
from src.utils import Util, null

import discord


class TimerCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "weather": dict(permission=const.Permission.USER.value, subcommand=False),
            "weatherforecast": dict(permission=const.Permission.USER.value, subcommand=False),
        })

    @staticmethod
    async def _weather(message, command, silent=False):
        """Get current weather using wttr.in
    Usage: !weather <city>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        city = "'" + ' '.join(command[1:]) + "'"
        try:
            r = Util.request(f"https://wttr.in/{city}?format=4")
            result = r.get()
            await Msg.response(message, result, silent)
            return result
        except Exception as e:
            return null(await Msg.response(message, f"Error while getting weather: {e}", silent))

    @staticmethod
    async def _weatherforecast(message, command, silent=False):
        """Get weather forecast using wttr.in
    Usage: !weatherforecast <city>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        city = "'" + ' '.join(command[1:]) + "'"
        try:
            r = Util.request(f"https://wttr.in/{city}.png?m")
            file_name = r.get_file(extension=".png")
            await Msg.response(message, None, silent, files=[discord.File(file_name)])
            os.unlink(file_name)
        except Exception as e:
            return null(await Msg.response(message, f"Error while getting weather: {e}", silent))
