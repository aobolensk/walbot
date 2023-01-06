import urllib.request
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
        bc.executor.commands["urlencode"] = Command(
            "string", "urlencode", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._urlencode)
        bc.executor.commands["takechars"] = Command(
            "string", "takechars", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._takechars)
        bc.executor.commands["dropchars"] = Command(
            "string", "dropchars", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._dropchars)
        bc.executor.commands["countchars"] = Command(
            "string", "countchars", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._countchars)
        bc.executor.commands["takewords"] = Command(
            "string", "takewords", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._takewords)
        bc.executor.commands["dropwords"] = Command(
            "string", "dropwords", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._dropwords)
        bc.executor.commands["countwords"] = Command(
            "string", "countwords", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._countwords)
        bc.executor.commands["takelines"] = Command(
            "string", "takelines", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._takelines)
        bc.executor.commands["droplines"] = Command(
            "string", "droplines", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._droplines)
        bc.executor.commands["countlines"] = Command(
            "string", "countlines", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._countlines)
        bc.executor.commands["tolower"] = Command(
            "string", "tolower", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._tolower)
        bc.executor.commands["toupper"] = Command(
            "string", "toupper", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._toupper)
        bc.executor.commands["join"] = Command(
            "string", "join", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._join)
        bc.executor.commands["eqwords"] = Command(
            "string", "eqwords", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._eqwords)
        bc.executor.commands["eqstrs"] = Command(
            "string", "eqstrs", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._eqstrs)

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
            stop = await Util.parse_int(
                execution_ctx, cmd_line[1], f"Stop parameter in range '{cmd_line[0]}' should be an integer")
        else:
            start = await Util.parse_int(
                execution_ctx, cmd_line[1], f"Start parameter in range '{cmd_line[0]}' should be an integer")
            stop = await Util.parse_int(
                execution_ctx, cmd_line[2], f"Stop parameter in range '{cmd_line[0]}' should be an integer")
            if len(cmd_line) == 4:
                step = await Util.parse_int(
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

    async def _urlencode(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Urlencode string
    Example: !urlencode hello, world!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[1:])
        result = urllib.request.quote(result.encode("cp1251"))
        await Command.send_message(execution_ctx, result)
        return result

    async def _takechars(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Take n characters of the string
    Examples:
        !takechars 2 hello
        Result: he
        !takechars -2 hello
        Result: lo"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:])
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = result[len(result) + num:]
        else:
            result = result[:num]
        await Command.send_message(execution_ctx, result)
        return result

    async def _dropchars(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Drop n characters of the string
    Examples:
        !dropchars 2 hello
        Result: llo
        !dropchars -2 hello
        Result: hel"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:])
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = result[:len(result) + num]
        else:
            result = result[num:]
        await Command.send_message(execution_ctx, result)
        return result

    async def _countchars(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Calculate length of the message
    Example: !countchars some text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = str(len(' '.join(cmd_line[1:])))
        await Command.send_message(execution_ctx, result)
        return result

    async def _takewords(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Take n words of the string
    Examples:
        !takewords 2 a b c
        Result: a b
        !takewords -2 a b c
        Result: b c"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:]).split()
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[len(result) + num:])
        else:
            result = ' '.join(result[:num])
        await Command.send_message(execution_ctx, result)
        return result

    async def _dropwords(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Drop n words of the string
    Examples:
        !dropwords 2 a b c
        Result: c
        !dropwords -2 a b c
        Result: a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:]).split()
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[:len(result) + num])
        else:
            result = ' '.join(result[num:])
        await Command.send_message(execution_ctx, result)
        return result

    async def _countwords(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Count amount of words
    Example: !countwords some text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = str(len(' '.join(cmd_line).split()) - 1)
        await Command.send_message(execution_ctx, result)
        return result

    async def _takelines(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Take n lines of the string
    Examples:
        !takelines 2 a
        b
        c
        Result: a
        b
        !takelines -2 a
        b
        c
        Result: b
        c"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:]).split('\n')
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[len(result) + num:])
        else:
            result = '\n'.join(result[:num])
        await Command.send_message(execution_ctx, result)
        return result

    async def _droplines(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Drop n lines of the string
    Examples:
        !droplines 2 a
        b
        c
        Result: c
        !droplines -2 a
        b
        c
        Result: a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[2:]).split('\n')
        num = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second argument of command '{cmd_line[0]}' should be an integer")
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[:len(result) + num])
        else:
            result = '\n'.join(result[num:])
        await Command.send_message(execution_ctx, result)
        return result

    async def _countlines(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Count amount of lines
    Example: !countlines some text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = str(len(' '.join(cmd_line).split('\n')))
        await Command.send_message(execution_ctx, result)
        return result

    async def _tolower(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Convert text to lower case
    Example: !tolower SoMe TeXt"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[1:]).lower()
        await Command.send_message(execution_ctx, result)
        return result

    async def _toupper(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Convert text to upper case
    Example: !toupper SoMe TeXt"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        result = ' '.join(cmd_line[1:]).upper()
        await Command.send_message(execution_ctx, result)
        return result

    async def _join(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Join words with string as separator
    Example: !join + 1 2 3 -> 1+2+3"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        separator = cmd_line[1]
        result = separator.join(cmd_line[2:])
        await Command.send_message(execution_ctx, result)
        return result

    async def _eqwords(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Check if two words are equal or not
    Example: !eqwords a b"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        result = "true" if cmd_line[1] == cmd_line[2] else "false"
        await Command.send_message(execution_ctx, result)
        return result

    async def _eqstrs(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Check if two strings separated by ';' are equal or not
    Example: !eqstrs a;b"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        options = ' '.join(cmd_line[1:]).split(';')
        if len(options) < 2:
            return await Command.send_message(execution_ctx, "Too few options to compare")
        if len(options) > 2:
            return await Command.send_message(execution_ctx, "Too many options to compare")
        result = "true" if options[0] == options[1] else "false"
        await Command.send_message(execution_ctx, result)
        return result
