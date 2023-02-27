import asyncio

from src import const
from src.config import bc
from tests.fixtures.context import BufferTestExecutionContext
from tests.fixtures.perm_cmd import PermFixtureCommands


def test_permission_commands_level_0(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(PermFixtureCommands())
    loop = asyncio.get_event_loop()
    ctx = BufferTestExecutionContext()
    loop.run_until_complete(bc.executor.commands["perm_user"].run(["perm_user"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_mod"].run(["perm_mod"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_admin"].run(["perm_admin"], ctx))
    captured = capsys.readouterr()
    assert captured.out == (
        "perm: user\n"
        "You don't have permission to call command 'perm_mod'\n"
        "You don't have permission to call command 'perm_admin'\n"
    )


def test_permission_commands_level_1(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(PermFixtureCommands())
    loop = asyncio.get_event_loop()
    ctx = BufferTestExecutionContext()
    ctx.permission_level = const.Permission.MOD
    loop.run_until_complete(bc.executor.commands["perm_user"].run(["perm_user"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_mod"].run(["perm_mod"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_admin"].run(["perm_admin"], ctx))
    captured = capsys.readouterr()
    assert captured.out == (
        "perm: user\n"
        "perm: mod\n"
        "You don't have permission to call command 'perm_admin'\n"
    )


def test_permission_commands_level_2(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(PermFixtureCommands())
    loop = asyncio.get_event_loop()
    ctx = BufferTestExecutionContext()
    ctx.permission_level = const.Permission.ADMIN
    loop.run_until_complete(bc.executor.commands["perm_user"].run(["perm_user"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_mod"].run(["perm_mod"], ctx))
    loop.run_until_complete(bc.executor.commands["perm_admin"].run(["perm_admin"], ctx))
    captured = capsys.readouterr()
    assert captured.out == (
        "perm: user\n"
        "perm: mod\n"
        "perm: admin\n"
    )
