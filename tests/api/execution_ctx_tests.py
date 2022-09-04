import inspect

from src.backend.discord.context import DiscordExecutionContext
from src.backend.telegram.context import TelegramExecutionContext
from tests.fixtures.context import BufferTestExecutionContext


def test_discord_execution_ctx_api_completeness():
    assert not inspect.isabstract(DiscordExecutionContext)


def test_telegram_execution_ctx_api_completeness():
    assert not inspect.isabstract(TelegramExecutionContext)


def test_buffertest_execution_ctx_api_completeness():
    assert not inspect.isabstract(BufferTestExecutionContext)
