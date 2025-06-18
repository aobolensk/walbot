import asyncio

from src.cmd.builtin import BuiltinCommands
from src.config import bc
from src import const
from tests.fixtures.context import BufferTestExecutionContext, TelegramTestExecutionContext


def test_empty_executor():
    assert bc.executor.commands == dict()


def test_ping_command(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        bc.executor.commands["ping"].run(["ping"], BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out == "🏓 Pong!  🏓\n"


def test_help_inserts_telegram_doc_link(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.get_event_loop()
    ctx = TelegramTestExecutionContext()
    loop.run_until_complete(bc.executor.commands["help"].run(["help"], ctx))
    captured = capsys.readouterr()
    assert const.TELEGRAM_COMMANDS_DOC_PATH in captured.out
