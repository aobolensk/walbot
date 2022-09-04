import inspect

from src.backend.discord.instance import DiscordBotInstance
from src.backend.repl.instance import ReplBotInstance
from src.backend.telegram.instance import TelegramBotInstance


def test_discord_bot_instance_api_completeness():
    assert not inspect.isabstract(DiscordBotInstance)


def test_telegram_bot_instance_api_completeness():
    assert not inspect.isabstract(TelegramBotInstance)


def test_repl_bot_instance_api_completeness():
    assert not inspect.isabstract(ReplBotInstance)
