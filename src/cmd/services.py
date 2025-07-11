import json
import os
import subprocess
import sys
from typing import List, Optional

from aiogoogletrans import Translator  # type:ignore

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
            subcommand=True, impl_func=self._netcheck, max_execution_time=60)
        bc.executor.commands["translate"] = Command(
            "services", "translate", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._translate, max_execution_time=10)
        bc.executor.commands["weather"] = Command(
            "services", "weather", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._weather, max_execution_time=15)
        bc.executor.commands["weatherforecast"] = Command(
            "services", "weatherforecast", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._weatherforecast, max_execution_time=15)

    async def _netcheck(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Check network and proxy settings
    Usage: !netcheck"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = ""
        try:
            r = Util.request(
                "https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py", use_proxy=True)
            p = subprocess.Popen(
                f"{sys.executable} - --json",
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            try:
                script_text = await r.get_text()
                output, err = p.communicate(input=script_text.encode("utf-8"), timeout=45)
            except subprocess.TimeoutExpired:
                p.kill()
                result += "Speedtest: operation timed out\n"
        except Exception as e:
            result += f"Speedtest: failed with error: {e}"
            if err:
                result += f" ({err.decode('utf-8')})"
            result += "\n"

        if output:
            try:
                j = json.loads(output)
            except json.JSONDecodeError as e:
                result += f"Speedtest: failed to parse output: {e}\n"
            result += f"IP: {j['client']['ip']}, country: {j['server']['cc']}\n"
            MBIT = 1024 * 1024
            result += (
                f"Speedtest: DL - {j['download'] / MBIT:.2f} Mbit/s, "
                f"UP - {j['upload'] / MBIT:.2f} Mbit/s\n"
            )
        else:
            result += "Speedtest did not respond\n"
        await Command.send_message(execution_ctx, result)
        return result

    async def _translate(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Translate text to specified language
    Usage: !translate <lang> <text>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return None
        translator = Translator(proxy=Util.proxy.http() or None)
        dst_language = cmd_line[1]
        text = " ".join(cmd_line[2:])
        try:
            translation = await translator.translate(text, dest=dst_language)
            result = translation.text
            await Command.send_message(execution_ctx, result)
            return result
        except ValueError as e:
            await Command.send_message(execution_ctx, f"ERROR! Could not translate text: {e}")
        return None

    async def _weather(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get current weather using wttr.in
    Usage: !weather <city>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        city = ' '.join(cmd_line[1:])
        try:
            r = Util.request(f"https://wttr.in/{city}?format=4")
            result = await r.get_text()
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
        return None

    async def _weatherforecast(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get weather forecast using wttr.in
    Usage: !weatherforecast <city>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        city = ' '.join(cmd_line[1:])
        try:
            r = Util.request(f"https://wttr.in/{city}.png?m")
            file_name = await r.get_file(extension=".png")
            await Command.send_message(execution_ctx, None, files=[file_name])
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
        return None
