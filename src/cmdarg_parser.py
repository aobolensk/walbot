import argparse
from typing import List, Optional

from src.api.execution_context import ExecutionContext
from src.config import bc


class _CmdArgSubParsersAction(argparse._SubParsersAction):
    def __init__(self, execution_ctx: ExecutionContext, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._execution_ctx = execution_ctx

    def add_parser(self, name, **kwargs):
        return super().add_parser(name, execution_ctx=self._execution_ctx, **kwargs)


class CmdArgParser(argparse.ArgumentParser):
    def __init__(self, execution_ctx: ExecutionContext, *args, **kwargs) -> None:
        kwargs["prog"] = ""  # Suppress executable name in the output
        kwargs["exit_on_error"] = False  # Forbid any exit on error
        super().__init__(*args, **kwargs)
        self.register('action', 'parsers', _CmdArgSubParsersAction)
        self._execution_ctx = execution_ctx
        self._error = False

    def parse_args(self, cmd_line: List[str]) -> Optional[argparse.Namespace]:  # type:ignore
        """Use cmd_line (required argument) as an input.
        Original argparse method is hidden.
        Return parsed args in Namespace class.
        If error happened return None"""
        self._error = False
        try:
            result = super().parse_args(cmd_line[1:])
        except argparse.ArgumentError as e:
            self.error(str(e))
            return None
        if self._error:
            return None
        return result

    def error(self, message) -> None:  # type:ignore
        # This function should not perform sys.exit
        """Original argparse method is hidden.
        Send error to text channel"""
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(message))
        self._error = True

    def exit(self, status=0, message=None) -> None:  # type:ignore
        # This function should not perform sys.exit
        """Original argparse method is hidden.
        Ignore argparse exit calls"""
        pass

    def print_help(self, file=None):
        """Print help to the channel where it was called"""
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(self.format_help()))
        self._error = True  # Do not return parsed args

    def print_usage(self, file=None):
        """Print usage to the channel where it was called"""
        bc.discord.background_loop.run_until_complete(self._execution_ctx.send_message(self.format_usage()))
        self._error = True  # Do not return parsed args

    def add_subparsers(self, **kwargs):
        return super().add_subparsers(parser_class=CmdArgParser, execution_ctx=self._execution_ctx, **kwargs)
