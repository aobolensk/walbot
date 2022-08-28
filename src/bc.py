import datetime
import enum
from collections import deque

from src.backend.discord.message_buffer import MessageBuffer
from src.executor import Executor
from src.plugin import PluginManager


@enum.unique
class DoNotUpdateFlag(enum.IntEnum):
    VOICE = 0
    DISCORD_REMINDER = enum.auto()
    TELEGRAM_REMINDER = enum.auto()
    POLL = enum.auto()
    TIMER = enum.auto()
    STOPWATCH = enum.auto()


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

    def __init__(self):
        self.deployment_time = datetime.datetime.now()
        self.commands = None
        self.config = None
        self.markov = None
        self.secret_config = None
        self.yaml_dumper = None
        self.do_not_update = [0] * len(DoNotUpdateFlag)
        self.timers = dict()
        self.stopwatches = dict()
        self.plugin_manager = PluginManager()
        self.message_buffer = MessageBuffer()
        self.instance_name = ""
        self.backends = {
            "discord": False,
            "telegram": False,
            "repl": False,
        }
        self.voice_ctx = self.VoiceCtx()
        self.executor = Executor()
