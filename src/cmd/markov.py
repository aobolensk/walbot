import re
from typing import List

from src import const
from src.api.command import BaseCmd, Command, ExecutionContext, Implementation
from src.config import bc


class MarkovCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self, commands) -> None:
        commands["markov"] = Command(
            "builtin", "markov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._markov)
        commands["markovgc"] = Command(
            "builtin", "markovgc", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._markovgc)
        commands["delmarkov"] = Command(
            "builtin", "delmarkov", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delmarkov)
        commands["findmarkov"] = Command(
            "builtin", "findmarkov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._findmarkov)

    def _markov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if len(cmd_line) > 1:
            result = ""
            for _ in range(const.MAX_MARKOV_ATTEMPTS):
                result = bc.markov.generate(word=cmd_line[-1])
                if len(result.split()) > 1:
                    break
            if result != "<Empty message was generated>":
                result = ' '.join(cmd_line[1:-1]) + ' ' + result
        else:
            result = bc.markov.generate()
        result = execution_ctx.disable_pings(result)
        Command.send_message(execution_ctx, result)
        return result

    def _markovgc(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = bc.markov.collect_garbage()
        result = f"Garbage collected {len(result)} items: {', '.join(result)}"
        Command.send_message(execution_ctx, result)
        return result

    def _delmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        regex = ' '.join(cmd_line[1:])
        try:
            removed = bc.markov.del_words(regex)
        except re.error as e:
            return Command.send_message(execution_ctx, f"Invalid regular expression: {e}")
        execution_ctx.send_message(f"Deleted {len(removed)} words from model: {removed}", suppress_embeds=True)

    def _findmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        regex = cmd_line[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            return Command.send_message(execution_ctx, f"Invalid regular expression: {e}")
        amount = len(found)
        if execution_ctx.platform == "discord":
            if not (len(cmd_line) > 2 and cmd_line[2] == '-f' and
                    bc.config.users[execution_ctx.message.author.id].permission_level >= const.Permission.MOD.value):
                found = found[:100]
        else:
            found = found[:100]
        execution_ctx.send_message(
            f"Found {amount} words in model: {found}"
            f"{f' and {amount - len(found)} more...' if amount - len(found) > 0 else ''}",
            suppress_embeds=True)
