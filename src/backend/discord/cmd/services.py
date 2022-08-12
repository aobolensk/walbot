"""Commands that get data from online services"""

import json
import os
import subprocess
import sys
from urllib.parse import urlparse

import discord
from googletrans import Translator
from httpcore import SyncHTTPProxy

from src import const
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
from src.exception import HTTPRequestException
from src.utils import Util, null


class TimerCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "netcheck": dict(permission=const.Permission.ADMIN.value, subcommand=True, max_execution_time=60),
            "translate": dict(permission=const.Permission.USER.value, subcommand=True, max_execution_time=10),
            "weather": dict(permission=const.Permission.USER.value, subcommand=True, max_execution_time=15),
            "weatherforecast": dict(permission=const.Permission.USER.value, subcommand=False, max_execution_time=15),
        })

    @staticmethod
    async def _netcheck(message, command, silent=False):
        """Check network and proxy settings
    Usage: !netcheck"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        try:
            r = Util.request(
                "https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py", use_proxy=True)
            p = subprocess.Popen(
                f"{sys.executable} - --json", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
            j = json.loads(p.communicate(input=r.get_text().encode("utf-8"))[0])
            result += f"IP: {j['client']['ip']}, country: {j['server']['cc']}\n"
            MBIT = 1024 * 1024
            result += (
                f"Speedtest: DL - {j['download'] / MBIT:.2f} Mbit/s, "
                f"UP - {j['upload'] / MBIT:.2f} Mbit/s\n"
            )
        except Exception as e:
            result += "Speedtest: failed with error: " + str(e) + "\n"
        await Msg.response(message, result, silent)

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
            result = translation.text
            await Msg.response(message, result, silent)
            return result
        except ValueError as e:
            await Msg.response(message, f"ERROR! Could not translate text: {e}", silent)

    @staticmethod
    async def _weather(message, command, silent=False):
        """Get current weather using wttr.in
    Usage: !weather <city>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        city = "'" + ' '.join(command[1:]) + "'"
        try:
            r = Util.request(f"https://wttr.in/{city}?format=4")
            result = r.get_text()
            await Msg.response(message, result, silent)
            return result
        except HTTPRequestException as e:
            if e.status_code == 404:
                await Msg.response(message, f"City not found: {city}", silent)
            else:
                return null(await Msg.response(message, f"Error while getting weather: {e}", silent))
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
        except HTTPRequestException as e:
            if e.status_code == 404:
                await Msg.response(message, f"City not found: {city}", silent)
            else:
                return null(await Msg.response(message, f"Error while getting weather: {e}", silent))
        except Exception as e:
            return null(await Msg.response(message, f"Error while getting weather: {e}", silent))
