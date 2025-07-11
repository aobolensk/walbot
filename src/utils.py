import asyncio
import datetime
import os
import tempfile
from enum import IntEnum
from typing import Any, Coroutine, Optional, Tuple

import requests
import yaml
from dateutil import tz

from src.api.command import Command
from src.api.execution_context import ExecutionContext
from src.exception import HTTPRequestException
from src.log import log


class TimeoutStatus(IntEnum):
    OK = 0
    TIMEOUT = 1


class Util:
    @staticmethod
    async def run_function_with_time_limit(coro: Coroutine, timeout: float) -> Tuple[TimeoutStatus, Optional[Any]]:
        try:
            return TimeoutStatus.OK, await asyncio.wait_for(coro, timeout)
        except asyncio.TimeoutError:
            return TimeoutStatus.TIMEOUT, None

    @staticmethod
    async def parse_int(execution_ctx: ExecutionContext, string: str, error_message: str):
        try:
            return int(string)
        except ValueError:
            return await Command.send_message(execution_ctx, error_message)

    @staticmethod
    async def parse_float(execution_ctx: ExecutionContext, string: str, error_message: str):
        try:
            return float(string)
        except ValueError:
            return await Command.send_message(execution_ctx, error_message)

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
        if not path:
            return ''
        result = ''
        for c in path:
            if c not in (os.sep, '/', '.'):
                result += c
            else:
                if result and result[-1] != '.':
                    result += '.'
        if result.endswith('.py'):
            result = result[:-3]
        if result.endswith('.'):
            result = result[:-1]
        return result

    @staticmethod
    def get_yaml() -> Any:
        """Get YAML loader and dumper type.
        yaml.Loader and yaml.Dumper are slower implementations than yaml.CLoader and yaml.CDumper"""
        try:
            loader = yaml.CLoader
            log.debug2("Using fast YAML Loader")
        except AttributeError:
            loader = yaml.Loader
            log.debug2("Using slow YAML Loader")
        try:
            dumper = yaml.CDumper
            log.debug2("Using fast YAML Dumper")
        except AttributeError:
            dumper = yaml.Dumper
            log.debug2("Using slow YAML Dumper")
        return loader, dumper

    @staticmethod
    def tmp_dir() -> str:
        """Get walbot temporary directory path inside system temporary directory
        and ensure it exists"""
        path = tempfile.gettempdir() + os.sep + "walbot"
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def cut_string(string: str, length: int) -> str:
        """Cut string to specified length"""
        if len(string) > length:
            return string[:(length - 3 if length > 3 else 0)] + "..."
        return string

    class proxy:
        def http() -> str:
            """Get HTTP proxy from environment"""
            return (
                os.environ.get("http_proxy") or
                os.environ.get("HTTP_PROXY") or ""
            )

        def https() -> str:
            """Get HTTPS proxy from environment"""
            return (
                os.environ.get("https_proxy") or
                os.environ.get("HTTPS_PROXY") or ""
            )

    class request:
        def __init__(self, url: str, timeout: float = 10, headers: dict = None, use_proxy: bool = True):
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

        async def get(self) -> requests.Response:
            """Get request"""
            return await asyncio.to_thread(
                requests.get,
                self.url,
                timeout=self.timeout,
                headers=self.headers,
                proxies=self.proxies,
            )

        async def get_text(self) -> str:
            """Get request text"""
            response = await self.get()
            if response.status_code == 200:
                return response.text
            else:
                log.error(f"Request failed with status code {response.status_code}")
                raise HTTPRequestException(response)

        async def get_file(self, extension='') -> str:
            """Get file request. Returns path to temporary file"""
            response = await self.get()
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(dir=Util.tmp_dir(), suffix=extension, delete=False) as tmp_file:
                    tmp_file.write(response.content)
                    return tmp_file.name
            else:
                log.error(f"Request failed with status code {response.status_code}")
                raise HTTPRequestException(response)

    @staticmethod
    def split_by_chunks(message, count):
        """Split message content by chunks with particular size"""
        for i in range(0, len(message), count):
            yield message[i:i + count]


class Time:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, tz: Optional[tz.tz.tzfile] = None) -> None:
        self._tz = tz

    def now(self) -> datetime.datetime:
        return datetime.datetime.now(tz=self._tz).replace(microsecond=0)


def null(*args, **kwargs) -> None:
    """Drop return value"""
    return None
