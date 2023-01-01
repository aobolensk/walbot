import json
from typing import List, Optional

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.bc import DoNotUpdateFlag
from src.config import bc


class _DebugCommand:
    def __init__(self, cmd: str, args: Optional[List[str]]) -> None:
        self._cmd = cmd
        self._args = args

    def run(self) -> str:
        diag_func_name = "diag_" + self._cmd
        if not hasattr(self, diag_func_name):
            return f"Unknown diagnostic '{diag_func_name}'"
        return getattr(self, diag_func_name)()

    def diag_ids(self) -> str:
        return json.dumps(bc.config.ids)

    def diag_do_not_update(self) -> str:
        return json.dumps(dict(zip([member.name for member in DoNotUpdateFlag], bc.do_not_update)))


class DebugCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["dbg"] = Command(
            "debug", "dbg", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._dbg)

    async def _dbg(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Debug command
    Example: !dbg <diagnostic-name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        debug_info = _DebugCommand(cmd_line[1], cmd_line[2:])
        result = debug_info.run()
        await Command.send_message(execution_ctx, result)
        return result
