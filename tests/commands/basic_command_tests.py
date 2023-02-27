import asyncio

from src.cmd.builtin import BuiltinCommands
from src.config import bc
from tests.fixtures.context import BufferTestExecutionContext


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
