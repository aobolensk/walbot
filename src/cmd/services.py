import json
import os
import subprocess
import sys
from typing import List, Optional
from urllib.parse import urlparse

import discord
from googletrans import Translator
from httpcore import SyncHTTPProxy

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.exception import HTTPRequestException
from src.utils import Util


class TimerCommands(BaseCmd):
    def bind(self):
        bc.executor.commands["netcheck"] = Command(
            "services", "netcheck", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=True, impl_func=self._netcheck)
        bc.executor.commands["translate"] = Command(
            "services", "translate", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._translate)
        bc.executor.commands["weather"] = Command(
            "services", "weather", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._weather)
        bc.executor.commands["weatherforecast"] = Command(
            "services", "weatherforecast", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._weatherforecast)

    async def _netcheck(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Check network and proxy settings
    Usage: !netcheck"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
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
        await Command.send_message(execution_ctx, result)

    async def _translate(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Translate text to specified language
    Usage: !translate <lang> <text>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
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
        dst_language = cmd_line[1]
        text = " ".join(cmd_line[2:])
        try:
            translation = translator.translate(text, dest=dst_language)
            result = translation.text
            await Command.send_message(execution_ctx, result)
            return result
        except ValueError as e:
            await Command.send_message(execution_ctx, f"ERROR! Could not translate text: {e}")

    async def _weather(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get current weather using wttr.in
    Usage: !weather <city>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        city = "'" + ' '.join(cmd_line[1:]) + "'"
        try:
            r = Util.request(f"https://wttr.in/{city}?format=4")
            result = r.get_text()
            await Command.send_message(execution_ctx, result)
            return result
        except HTTPRequestException as e:
            if e.status_code == 404:
                await Command.send_message(execution_ctx, f"City not found: {city}")
            else:
                result = f"Error while getting weather: {e}"
                await Command.send_message(execution_ctx, result)
                return result
        except Exception as e:
            result = f"Error while getting weather: {e}"
            await Command.send_message(execution_ctx, result)
            return result

    async def _weatherforecast(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Get weather forecast using wttr.in
    Usage: !weatherforecast <city>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        city = "'" + ' '.join(cmd_line[1:]) + "'"
        try:
            r = Util.request(f"https://wttr.in/{city}.png?m")
            file_name = r.get_file(extension=".png")
            await Command.send_message(execution_ctx, None, files=[discord.File(file_name)])
            os.unlink(file_name)
        except HTTPRequestException as e:
            if e.status_code == 404:
                await Command.send_message(execution_ctx, f"City not found: {city}")
            else:
                result = f"Error while getting weather: {e}"
                await Command.send_message(execution_ctx, result)
                return result
        except Exception as e:
            result = f"Error while getting weather: {e}"
            await Command.send_message(execution_ctx, result)
            return result