import re

from enum import Enum, unique


config_path = "config.yaml"
markov_path = "markov.yaml"
secret_config_path = "secret.yaml"

MAX_POLL_OPTIONS = 20
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000

FILENAME_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9_-]+$')
REMINDER_TIME_FORMAT = "%Y-%m-%d %H:%M"
EMOJI_REGEX = re.compile(r'<:(\w*):(\d*)>')
USER_ID_REGEX = re.compile(r'<@!(\d*)>')


@unique
class Permission(Enum):
    USER = 0
    MOD = 1
    ADMIN = 2
