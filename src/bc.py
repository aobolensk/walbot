import datetime
import enum
from collections import deque
from typing import TYPE_CHECKING, Optional

from src.executor import Executor
from src.message_cache import MessageCache
from src.plugin import PluginManager

if TYPE_CHECKING:
    import asyncio

    import telegram.ext
    from discord import ClientUser

    from src.backend.discord.commands import Commands
    from src.config import Config, SecretConfig
    from src.markov import Markov


@enum.unique
class DoNotUpdateFlag(enum.IntEnum):
    VOICE = 0
    DISCORD_REMINDER = enum.auto()
    TELEGRAM_REMINDER = enum.auto()
    POLL = enum.auto()
    TIMER = enum.auto()
    STOPWATCH = enum.auto()
    # Reserved fields for using in custom scenarios (e.g. user plugins)
    RESERVED1 = enum.auto()
    RESERVED2 = enum.auto()
    RESERVED3 = enum.auto()


class BotController:
    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    class VoiceCtx:
        def __init__(self):
            self.client = None
            self.queue = deque()
            self.auto_rejoin_channel = None
            self.current_video = None

    class Discord:
        def __init__(self) -> None:
            self.bot_user: 'Optional[ClientUser]' = None
            self.commands: 'Commands' = None
            self.get_channel = None
            self.get_user = None
            self.background_loop: 'Optional[asyncio.AbstractEventLoop]' = None
            self.change_status = None
            self.change_presence = None
            self.latency = None

    class Telegram:
        def __init__(self) -> None:
            self.bot_username: 'Optional[str]' = None
            self.dispatcher: 'Optional[telegram.ext.Dispatcher]' = None
            self.handlers = dict()

    class Repl:
        def __init__(self) -> None:
            pass

    def __init__(self):
        self.deployment_time = datetime.datetime.now()
        self.config: 'Optional[Config]' = None
        self.markov: 'Optional[Markov]' = None
        self.secret_config: 'Optional[SecretConfig]' = None
        self.yaml_dumper = None
        self.do_not_update = [0] * len(DoNotUpdateFlag)
        self.timers = dict()
        self.stopwatches = dict()
        self.backends = {
            "discord": False,
            "telegram": False,
            "repl": False,
        }
        self.voice_ctx = self.VoiceCtx()
        self.executor = Executor()
        self.discord = self.Discord()
        self.telegram = self.Telegram()
        self.repl = self.Repl()
        self.plugin_manager = PluginManager()
        self.message_cache = MessageCache()
