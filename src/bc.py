import datetime
from collections import deque
from enum import IntEnum

from src.message_buffer import MessageBuffer
from src.plugin import PluginManager


class DoNotUpdateFlag(IntEnum):
    VOICE = 0
    REMINDER = 1
    POLL = 2
    TIMER = 3


class BotController:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.background_events = []
        self.deployment_time = datetime.datetime.now()
        self.background_loop = None
        self.commands = None
        self.config = None
        self.markov = None
        self.secret_config = None
        self.yaml_dumper = None
        self.voice_client = None
        self.voice_client_queue = deque()
        self.do_not_update = [0] * len(DoNotUpdateFlag)
        self.timers = dict()
        self.plugin_manager = PluginManager()
        self.message_buffer = MessageBuffer()
