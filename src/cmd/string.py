from typing import List

from src import const, emoji
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc


class StringCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["emojify"] = Command(
            "string", "emojify", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._emojify)
        bc.executor.commands["demojify"] = Command(
            "string", "demojify", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._demojify)

    async def _emojify(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Emojify text
    Example: !emojify Hello!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        text = ' '.join(cmd_line[1:]).lower()
        result = ""
        is_emoji = False
        for word in text:
            if not is_emoji:
                result += ' '
            if word in emoji.text_to_emoji.keys():
                is_emoji = True
                result += emoji.text_to_emoji[word] + ' '
            else:
                is_emoji = False
                result += word
        result = result.strip()
        await Command.send_message(execution_ctx, result)
        return result

    async def _demojify(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Demojify text
    Example: !demojify 🇭 🇪 🇱 🇱 🇴"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        text = ' '.join(cmd_line[1:])
        result = ""
        i = 0
        while i < len(text):
            if text[i] in emoji.emoji_to_text.keys():
                result += emoji.emoji_to_text[text[i]]
                i += 1
            else:
                result += text[i]
            i += 1
        result = result.strip()
        await Command.send_message(execution_ctx, result)
        return result
