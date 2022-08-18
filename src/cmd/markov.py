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
            subcommand=False, impl_func=self._markov)

    def _markov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show bot uptime"""
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
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
