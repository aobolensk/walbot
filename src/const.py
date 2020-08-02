import re

from enum import Enum, unique

CONFIG_VERSION = '0.0.10'
MARKOV_CONFIG_VERSION = '0.0.1'
SECRET_CONFIG_VERSION = '0.0.1'

BOT_CACHE_FILE_PATH = ".bot_cache"
NOHUP_FILE_PATH = "nohup.out"

CONFIG_PATH = "config.yaml"
MARKOV_PATH = "markov.yaml"
SECRET_CONFIG_PATH = "secret.yaml"
COMMANDS_DOC_PATH = "docs/Commands.md"

MAX_POLL_OPTIONS = 20
MAX_RANGE_ITERATIONS = 500
DISCORD_MAX_EMBED_FILEDS_COUNT = 25
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000
MAX_MARKOV_ATTEMPTS = 64

ALNUM_STRING_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9 ]+$')
FILENAME_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9_-]+$')
REMINDER_TIME_FORMAT = "%Y-%m-%d %H:%M"
EMOJI_REGEX = re.compile(r'<:(\w*):(\d*)>')
USER_ID_REGEX = re.compile(r'<@!(\d*)>')
ROLE_ID_REGEX = re.compile(r'<@&(\d*)>')
INTEGER_NUMBER = re.compile(r'[-+]?\d+')
ARGS_REGEX = re.compile(r'@args(\d*)-(\d*)@')

ROLE_EVERYONE = "@everyone"
ROLE_HERE = "@here"


@unique
class Permission(Enum):
    USER = 0
    MOD = 1
    ADMIN = 2
