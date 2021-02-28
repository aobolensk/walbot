import enum
import re

DISCORD_LIB_VERSION = '1.6.0'

CONFIG_VERSION = '0.0.20'
MARKOV_CONFIG_VERSION = '0.0.6'
SECRET_CONFIG_VERSION = '0.0.1'

BOT_CACHE_FILE_PATH = ".bot_cache"
NOHUP_FILE_PATH = "nohup.out"

GIT_REPO_LINK = "https://github.com/aobolensk/walbot"

CONFIG_PATH = "config.yaml"
MARKOV_PATH = "markov.yaml"
SECRET_CONFIG_PATH = "secret.yaml"
COMMANDS_DOC_PATH = "docs/Commands.md"
LOGS_DIRECTORY = "logs"

MAX_POLL_OPTIONS = 20
MAX_RANGE_ITERATIONS = 500
MAX_LOG_FILESIZE = 3 * 1024 * 1024
DISCORD_MAX_EMBED_FILEDS_COUNT = 25
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000
MAX_MARKOV_ATTEMPTS = 64

REMINDER_POLLING_INTERVAL = 30  # seconds
AUTOUPDATE_CHECK_INTERVAL = 10 * 60  # seconds

ALNUM_STRING_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9 ]+$')
FILENAME_REGEX = re.compile('^[A-Za-zА-Яа-яЁё0-9_-]+$')
LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(filename)s: %(message)s"
REMINDER_DATE_FORMAT = "%Y-%m-%d"
REMINDER_TIME_FORMAT = "%Y-%m-%d %H:%M"
EMOJI_REGEX = re.compile(r'<:(\w*):(\d*)>')
USER_ID_REGEX = re.compile(r'<@!(\d*)>')
ROLE_ID_REGEX = re.compile(r'<@&(\d*)>')
INTEGER_NUMBER = re.compile(r'[-+]?\d+')
ARGS_REGEX = re.compile(r'@args(\d*)-(\d*)@')
REMINDER_IN_REGEX = re.compile(r'(([0-9]*)w)?(([0-9]*)d)?(([0-9])*h)?(([0-9])*m)?')

ROLE_EVERYONE = "@everyone"
ROLE_HERE = "@here"


@enum.unique
class Permission(enum.IntEnum):
    USER = 0
    MOD = 1
    ADMIN = 2


@enum.unique
class ExitStatus(enum.IntEnum):
    NO_ERROR = 0
    GENERAL_ERROR = 1
    CONFIG_FILE_ERROR = 2


class LogLevel(enum.IntEnum):
    # Logging levels: https://docs.python.org/3/library/logging.html#logging-levels
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    DEBUG2 = 9
    DEBUG3 = 8
    NOTSET = 0
