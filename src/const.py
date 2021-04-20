import enum
import re

import src.version as ver


def _extract_discord_lib_version_from_requirements_txt():
    with open("requirements.txt", "r") as f:
        for line in f:
            if line.startswith("discord.py=="):
                return line.split('==')[1].strip()
    return "<unknown>"


DISCORD_LIB_VERSION = _extract_discord_lib_version_from_requirements_txt()

CONFIG_VERSION = ver.CONFIG_VERSION
MARKOV_CONFIG_VERSION = ver.MARKOV_CONFIG_VERSION
SECRET_CONFIG_VERSION = ver.SECRET_CONFIG_VERSION

BOT_CACHE_FILE_PATH = ".bot_cache"
NOHUP_FILE_PATH = "nohup.out"

GIT_REPO_LINK = "https://github.com/aobolensk/walbot"

CONFIG_PATH = "config.yaml"
MARKOV_PATH = "markov.yaml"
SECRET_CONFIG_PATH = "secret.yaml"
COMMANDS_DOC_PATH = "docs/Commands.md"
LOGS_DIRECTORY = "logs"
IMAGES_DIRECTORY = "images"

MAX_POLL_OPTIONS = 20
MAX_RANGE_ITERATIONS = 500
MAX_LOG_FILESIZE = 3 * 1024 * 1024
DISCORD_MAX_EMBED_FILEDS_COUNT = 25
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000
MAX_MARKOV_ATTEMPTS = 64
MAX_SUBCOMMAND_DEPTH = 256

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
# Reference: https://gist.github.com/Alex-Just/e86110836f3f93fe7932290526529cd1#gistcomment-3208085
UNICODE_EMOJI_REGEX = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "]"
)


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
