from typing import List, Optional

from src import const, emoji
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Util


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
        bc.executor.commands["range"] = Command(
            "string", "range", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._range)

    async def _emojify(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
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

    async def _demojify(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
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

    async def _range(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Generate range of numbers
    Examples:
        !range <stop>
        !range <start> <stop>
        !range <start> <stop> <step>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=4):
            return
        start, stop, step = 0, 0, 1
        if len(cmd_line) == 2:
            stop = await Util.parse_int_for_command(
                execution_ctx, cmd_line[1], f"Stop parameter in range '{cmd_line[0]}' should be an integer")
        else:
            start = await Util.parse_int_for_command(
                execution_ctx, cmd_line[1], f"Start parameter in range '{cmd_line[0]}' should be an integer")
            stop = await Util.parse_int_for_command(
                execution_ctx, cmd_line[2], f"Stop parameter in range '{cmd_line[0]}' should be an integer")
            if len(cmd_line) == 4:
                step = await Util.parse_int_for_command(
                    execution_ctx, cmd_line[3], f"Step parameter in range '{cmd_line[0]}' should be an integer")
        if start is None or stop is None or step is None:
            return
        result = ''
        for iteration, number in enumerate(range(start, stop, step)):
            if iteration >= const.MAX_RANGE_ITERATIONS:
                result = f"Range iteration limit ({const.MAX_RANGE_ITERATIONS}) has exceeded"
                break
            result += str(number) + ' '
        else:
            result = result[:-1]
        await Command.send_message(execution_ctx, result)
        return result
