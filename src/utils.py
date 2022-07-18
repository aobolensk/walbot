import asyncio
import os
import subprocess
import tempfile
from enum import IntEnum
from typing import Any, Coroutine, Optional, Tuple

import requests
import yaml

from src.log import log
from src.backend.discord.message import Msg


class TimeoutStatus(IntEnum):
    OK = 0
    TIMEOUT = 1


class Util:
    @staticmethod
    async def check_args_count(message, command, silent, min=None, max=None):
        if min and len(command) < min:
            await Msg.response(message, f"Too few arguments for command '{command[0]}'", silent)
            return False
        if max and len(command) > max:
            await Msg.response(message, f"Too many arguments for command '{command[0]}'", silent)
            return False
        return True

    @staticmethod
    async def run_function_with_time_limit(coro: Coroutine, timeout: float) -> Tuple[TimeoutStatus, Optional[Any]]:
        try:
            return TimeoutStatus.OK, await asyncio.wait_for(coro, timeout)
        except asyncio.TimeoutError:
            return TimeoutStatus.TIMEOUT, None

    @staticmethod
    async def parse_int(message, string, error_message, silent):
        try:
            return int(string)
        except ValueError:
            await Msg.response(message, error_message, silent)
            return

    @staticmethod
    async def parse_float(message, string, error_message, silent):
        try:
            return float(string)
        except ValueError:
            await Msg.response(message, error_message, silent)
            return

    @staticmethod
    def check_version(name, actual, expected, solutions=None, fatal=True):
        if actual == expected:
            return True
        if not fatal:
            log.warning(f"{name} versions mismatch. Expected: {expected}, but actual: {actual}")
        else:
            log.error(f"{name} versions mismatch. Expected: {expected}, but actual: {actual}")
        if solutions:
            log.info("Possible solutions:")
            for solution in solutions:
                log.info(f" - {solution}")
        return not fatal

    @staticmethod
    async def run_external_command(message, cmd_line, silent=False):
        result = ""
        try:
            log.debug(f"Processing external command: '{cmd_line}'")
            process = subprocess.run(cmd_line, shell=True, check=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
            log.debug(f"External command '{cmd_line}' finished execution with return code: {process.returncode}")
            result = process.stdout.decode("utf-8")
            await Msg.response(message, result, silent)
        except subprocess.CalledProcessError as e:
            await Msg.response(message, f"<Command failed with error code {e.returncode}>", silent)
        return result

    @staticmethod
    def read_config_file(path: str) -> Any:
        """Read YAML configuration file"""
        yaml_loader, _ = Util.get_yaml()
        if not os.path.isfile(path):
            return None
        with open(path, 'r') as f:
            try:
                return yaml.load(f.read(), Loader=yaml_loader)
            except Exception:
                log.error(f"File '{path}' can not be read!", exc_info=True)
        return None

    @staticmethod
    def path_to_module(path: str) -> str:
        """Convert OS path to Python module"""
        result = ''
        for c in path:
            if c not in (os.pathsep, '.') or result[-1] != '.':
                result += c
        return result

    @staticmethod
    def get_yaml(verbose: bool = False) -> Any:
        """Get YAML loader and dumper type.
        yaml.Loader and yaml.Dumper are slower implementations than yaml.CLoader and yaml.CDumper"""
        try:
            loader = yaml.CLoader
            if verbose:
                log.debug("Using fast YAML Loader")
        except AttributeError:
            loader = yaml.Loader
            if verbose:
                log.debug("Using slow YAML Loader")
        try:
            dumper = yaml.CDumper
            if verbose:
                log.debug("Using fast YAML Dumper")
        except AttributeError:
            dumper = yaml.Dumper
            if verbose:
                log.debug("Using slow YAML Dumper")
        return loader, dumper

    @staticmethod
    def tmp_dir() -> str:
        """Get walbot temporary directory path inside system temporary directory"""
        return tempfile.gettempdir() + os.sep + "walbot"

    @staticmethod
    def cut_string(string: str, length: int) -> str:
        """Cut string to specified length"""
        if len(string) > length:
            return string[:(length - 3 if length > 3 else 0)] + "..."
        return string

    class proxy:
        def http() -> Optional[str]:
            """Get HTTP proxy from environment"""
            return (
                os.environ.get("http_proxy") or
                os.environ.get("HTTP_PROXY")
            )

        def https() -> Optional[str]:
            """Get HTTPS proxy from environment"""
            return (
                os.environ.get("https_proxy") or
                os.environ.get("HTTPS_PROXY")
            )

    class request:
        def __init__(self, url: str, timeout: float = 10, headers: dict = None, use_proxy: bool = False):
            self.url = url
            self.timeout = timeout
            self.headers = headers
            if use_proxy:
                self.proxies = {
                    "http": Util.proxy.http(),
                    "https": Util.proxy.https()
                }
            else:
                self.proxies = None

        def get(self) -> str:
            """Get request"""
            return requests.get(self.url, timeout=self.timeout, headers=self.headers, proxies=self.proxies)

        def get_text(self) -> str:
            """Get request text"""
            return self.get().text

        def get_file(self, extension='') -> str:
            """Get file request. Returns path to temporary file"""
            response = requests.get(self.url, timeout=self.timeout, headers=self.headers, proxies=self.proxies)
            with tempfile.NamedTemporaryFile(dir=Util.tmp_dir(), suffix=extension, delete=False) as tmp_file:
                tmp_file.write(response.content)
                return tmp_file.name


def null(*args, **kwargs):
    """Drop return value"""
    return
