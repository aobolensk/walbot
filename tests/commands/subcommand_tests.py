import asyncio

from src.cmd.builtin import BuiltinCommands
from src.cmd.math import MathCommands
from src.config import bc
from src.test import BufferTestExecutionContext


def test_ping_command_with_subcommand(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(
        bc.executor.commands["echo"].run(["echo", "$(ping)"], BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out == "🏓 Pong!  🏓\n"


def test_ping_command_with_multilevel_nested_subcommands(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.new_event_loop()
    cmd = "echo $(echo Test 1)"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    cmd = "echo $(echo $(echo Test 2))"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    cmd = "echo $(echo $(echo $(echo Test 3)))"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    cmd = "echo $(echo $(echo $(echo $(echo Test 4))))"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out == (
        "Test 1\n"
        "Test 2\n"
        "Test 3\n"
        "Test 4\n"
    )


def test_command_that_does_not_support_subcommand_usage(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.new_event_loop()
    cmd = "echo $(about)"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out.strip() == "Command 'about' can not be used as subcommand"


def test_empty_subcommand_returns_nothing(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    loop = asyncio.new_event_loop()
    cmd = "echo $()"
    loop.run_until_complete(
        bc.executor.commands[cmd.split()[0]].run(cmd.split(), BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out.strip() == ""


def test_if_and_calc_commands_as_subcommands(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    bc.executor.add_module(MathCommands())
    loop = asyncio.new_event_loop()
    loop.run_until_complete(bc.executor.commands["echo"].run(
        "echo $(if $(calc 2 < 3) less;not less)".split(" "), BufferTestExecutionContext()))
    loop.run_until_complete(bc.executor.commands["echo"].run(
        "echo $(if $(calc 2 == 3) equal;not equal)".split(" "), BufferTestExecutionContext()))
    loop.run_until_complete(bc.executor.commands["echo"].run(
        "echo $(if $(calc 2 > 3) greater;not greater)".split(" "), BufferTestExecutionContext()))
    captured = capsys.readouterr()
    assert captured.out == (
        "less\n"
        "not equal\n"
        "not greater\n"
    )
