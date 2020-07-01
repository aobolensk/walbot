import re

from enum import Enum, unique

CONFIG_VERSION = '0.0.4'
MARKOV_CONFIG_VERSION = '0.0.1'
SECRET_CONFIG_VERSION = '0.0.1'

CONFIG_PATH = "config.yaml"
MARKOV_PATH = "markov.yaml"
SECRET_CONFIG_PATH = "secret.yaml"

MAX_POLL_OPTIONS = 20
MAX_RANGE_ITERATIONS = 500
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000
MAX_MARKOV_ATTEMPTS = 64

FILENAME_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9_-]+$')
REMINDER_TIME_FORMAT = "%Y-%m-%d %H:%M"
EMOJI_REGEX = re.compile(r'<:(\w*):(\d*)>')
USER_ID_REGEX = re.compile(r'<@!(\d*)>')
ROLE_ID_REGEX = re.compile(r'<@&(\d*)>')
INTEGER_NUMBER = re.compile(r'[-+]?\d+')

ROLE_EVERYONE = "@everyone"
ROLE_HERE = "@here"


@unique
class Permission(Enum):
    USER = 0
    MOD = 1
    ADMIN = 2
