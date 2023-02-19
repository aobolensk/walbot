import argparse
from typing import List, Optional

from src.api.execution_context import ExecutionContext
from src.config import bc


class CmdArgParser(argparse.ArgumentParser):
    def __init__(self, execution_ctx: ExecutionContext) -> None:
        super().__init__(prog="")
        self._execution_ctx = execution_ctx
        self._error = False

    def parse_args(self, cmd_line: List[str]) -> Optional[argparse.Namespace]:
        """Original argparse method is hidden.
        Use cmd_line (required argument) as an input.
        Return parsed args in Namespace class.
        If error happened return None"""
        self._error = False
        result = super().parse_args(cmd_line[1:])
        if self._error:
            return None
        return result

    def error(self, message) -> None:
        """Original argparse method is hidden.
        Send error to text channel"""
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(message))
        self._error = True

    def exit(self, status=0, message=None) -> None:
        """Original argparse method is hidden.
        Ignore argparse exit calls"""
        pass

    def print_help(self, file=None):
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(self.format_help()))
        self._error = True  # Do not return parsed args

    def print_usage(self, file=None):
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(self.format_usage()))
        self._error = True  # Do not return parsed args
