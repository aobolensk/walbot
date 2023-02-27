from typing import List

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc


class PermFixtureCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["perm_user"] = Command(
            "fixture", "perm_user", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._perm_user)
        bc.executor.commands["perm_mod"] = Command(
            "fixture", "perm_mod", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=True, impl_func=self._perm_mod)
        bc.executor.commands["perm_admin"] = Command(
            "fixture", "perm_admin", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=True, impl_func=self._perm_admin)

    async def _perm_user(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Command for permission level >= user"""
        await Command.send_message(execution_ctx, "perm: user")

    async def _perm_mod(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Command for permission level >= mod"""
        await Command.send_message(execution_ctx, "perm: mod")

    async def _perm_admin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Command for permission level >= admin"""
        await Command.send_message(execution_ctx, "perm: admin")
