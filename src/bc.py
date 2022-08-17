import datetime
from collections import deque
from enum import IntEnum

from src.api.command import Executor
from src.backend.discord.message_buffer import MessageBuffer
from src.plugin import PluginManager


class DoNotUpdateFlag(IntEnum):
    VOICE = 0
    REMINDER = 1
    POLL = 2
    TIMER = 3
    STOPWATCH = 4


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
        self.background_events = []
        self.deployment_time = datetime.datetime.now()
        self.background_loop = None
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
