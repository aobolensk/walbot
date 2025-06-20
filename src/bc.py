import enum
import itertools
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Union

from src import const
from src.executor import Executor
from src.log import log
from src.message_cache import MessageCache
from src.plugin import PluginManager
from src.utils import Time

if TYPE_CHECKING:
    import asyncio

    import telegram.ext
    import yaml
    from discord import ClientUser
    from telegram.ext import CommandHandler

    from src.backend.discord.commands import Commands
    from src.config import Config, SecretConfig
    from src.markov import Markov


@enum.unique
class DoNotUpdateFlag(enum.IntEnum):
    DISCORD_REMINDER = enum.auto()
    TELEGRAM_REMINDER = enum.auto()
    POLL = enum.auto()
    TIMER = enum.auto()
    STOPWATCH = enum.auto()
    BUILTIN_PLUGIN_VQ = enum.auto()
    # Reserved fields for using in custom scenarios (e.g. user plugins)
    RESERVED1 = enum.auto()
    RESERVED2 = enum.auto()
    RESERVED3 = enum.auto()


class BotController:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    class Discord:
        def __init__(self) -> None:
            self.bot_user: 'Optional[ClientUser]' = None
            self.commands: 'Commands' = None
            self.get_channel: Optional[Callable] = None
            self.get_user: Optional[Callable] = None
            self.background_loop: 'Optional[asyncio.AbstractEventLoop]' = None
            self.change_status: Optional[Callable] = None
            self.change_presence: Optional[Callable] = None
            self.latency: Optional[Callable] = None
            self.bot_user_id: Optional[int] = None
            self.guilds = None

    class Telegram:
        def __init__(self) -> None:
            self.bot_username: 'Optional[str]' = None
            self.app: 'Optional[telegram.ext.Application]' = None
            self.handlers: 'Dict[str, CommandHandler]' = dict()

    class Repl:
        def __init__(self) -> None:
            pass

    class Backend:
        def __init__(self) -> None:
            self._backends: Dict[const.BotBackend, bool] = dict(zip(
                [backend for backend in const.BotBackend][1:], itertools.repeat(False)))

        def set_running(self, backend: const.BotBackend, new_state: bool, user_data_msg: str = "") -> None:
            if new_state:
                log.info(f"Backend controller: {str(backend).title()} instance has started!")
                if user_data_msg:
                    log.info(f"[{backend}] Logged in as: {user_data_msg}")
            else:
                log.info(f"Backend controller: {str(backend).title()} instance has stopped!")
            self._backends[backend] = new_state

        def is_running(self, backend: const.BotBackend) -> bool:
            return self._backends[backend]

    def __init__(self):
        self.deployment_time = Time().now()
        self.config: 'Optional[Config]' = None
        self.markov: 'Optional[Markov]' = None
        self.secret_config: 'Optional[SecretConfig]' = None
        self.yaml_loader: 'Optional[Union[yaml.Loader, yaml.CLoader]]' = None
        self.yaml_dumper: 'Optional[Union[yaml.Dumper, yaml.CDumper]]' = None
        self.do_not_update: List[Union[int, bool]] = [0] * len(DoNotUpdateFlag)
        self.timers: Dict[int, bool] = dict()
        self.stopwatches: Dict[int, bool] = dict()
        self.executor = Executor()
        self.discord = self.Discord()
        self.telegram = self.Telegram()
        self.repl = self.Repl()
        self.plugin_manager = PluginManager(self.executor)
        self.message_cache = MessageCache()
        self.be = self.Backend()
