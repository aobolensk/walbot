import asyncio

from src.api.command import Command
from tests.fixtures.context import BufferTestExecutionContext


def test_check_args_count_min_zero():
    ctx = BufferTestExecutionContext()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(
        Command.check_args_count(ctx, ["cmd", "arg"], min=0)
    )
    assert result


def test_check_args_count_max_zero(capsys):
    ctx = BufferTestExecutionContext()
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(
        Command.check_args_count(ctx, ["cmd", "arg"], max=0)
    )
    assert not result
    captured = capsys.readouterr()
    assert captured.out.strip() == "Too many arguments for command 'cmd'"
