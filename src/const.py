from enum import Enum, unique


config_path = "config.yaml"
markov_path = "markov.yaml"
secret_config_path = "secret.yaml"

MAX_POLL_OPTIONS = 20
DISCORD_MAX_MESSAGE_LENGTH = 2000
MAX_MESSAGE_HISTORY_DEPTH = 1000

FILENAME_REGEX = '^[A-Za-zА-Яа-яЁё0-9_-]+$'
REMINDER_TIME_FORMAT = "%Y-%m-%d %H:%M"
EMOJI_REGEX = r'<:(\w*):(\d*)>'


@unique
class Permission(Enum):
    USER = 0
    MOD = 1
    ADMIN = 2
