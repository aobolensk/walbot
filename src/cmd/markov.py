import asyncio
import os
import re
from typing import List, Optional

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Util, null


class MarkovCommands(BaseCmd):
    def bind(self) -> None:
        bc.executor.commands["markov"] = Command(
            "markov", "markov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._markov)
        bc.executor.commands["markovgc"] = Command(
            "markov", "markovgc", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._markovgc)
        bc.executor.commands["delmarkov"] = Command(
            "markov", "delmarkov", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delmarkov)
        bc.executor.commands["findmarkov"] = Command(
            "markov", "findmarkov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._findmarkov)
        bc.executor.commands["getmarkovword"] = Command(
            "markov", "getmarkovword", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._getmarkovword)
        bc.executor.commands["dropmarkov"] = Command(
            "markov", "dropmarkov", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._dropmarkov)
        bc.executor.commands["statmarkov"] = Command(
            "markov", "statmarkov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._statmarkov)
        bc.executor.commands["inspectmarkov"] = Command(
            "markov", "inspectmarkov", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._inspectmarkov)
        bc.executor.commands["addmarkovfilter"] = Command(
            "markov", "addmarkovfilter", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addmarkovfilter)
        bc.executor.commands["listmarkovfilter"] = Command(
            "markov", "listmarkovfilter", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._listmarkovfilter)
        bc.executor.commands["delmarkovfilter"] = Command(
            "markov", "delmarkovfilter", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delmarkovfilter)
        bc.executor.commands["addmarkovignoredprefix"] = Command(
            "markov", "addmarkovignoredprefix", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addmarkovignoredprefix)
        bc.executor.commands["listmarkovignoredprefix"] = Command(
            "markov", "listmarkovignoredprefix", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._listmarkovignoredprefix)
        bc.executor.commands["delmarkovignoredprefix"] = Command(
            "markov", "delmarkovignoredprefix", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delmarkovignoredprefix)

    async def _markov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Generate message using Markov chain
    Example: !markov"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1):
            return None
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
        if execution_ctx.platform == const.BotBackend.DISCORD:
            if not bc.config.discord.guilds[execution_ctx.message.channel.guild.id].markov_pings:
                result = await execution_ctx.disable_pings(result)
        await Command.send_message(execution_ctx, result)
        return result

    async def _markovgc(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = bc.markov.collect_garbage()
        result = f"Garbage collected {len(result)} items: {', '.join(result)}"
        await Command.send_message(execution_ctx, result)
        return result

    async def _delmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        regex = ' '.join(cmd_line[1:])
        try:
            removed = bc.markov.del_words(regex)
        except re.error as e:
            return null(await Command.send_message(execution_ctx, f"Invalid regular expression: {e}"))
        await execution_ctx.send_message(f"Deleted {len(removed)} words from model: {removed}", suppress_embeds=True)

    async def _findmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Match words in Markov model using regex. If you have permission level >= 1,
        you can add -f flag to show full list of found words
    Examples:
        !findmarkov hello
        !findmarkov hello -f"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return None
        regex = cmd_line[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            return null(await Command.send_message(execution_ctx, f"Invalid regular expression: {e}"))
        amount = len(found)
        if not (len(cmd_line) > 2 and cmd_line[2] == '-f' and
                execution_ctx.permission_level >= const.Permission.MOD.value):
            found = found[:100]
        await execution_ctx.send_message(
            f"Found {amount} words in model: {found}"
            f"{f' and {amount - len(found)} more...' if amount - len(found) > 0 else ''}",
            suppress_embeds=True)

    async def _getmarkovword(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Get particular word from Markov model by regex
    Examples:
        !getmarkovword hello -a <- get amount of found words
        !getmarkovword hello 0 <- get word by index"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return None
        regex = cmd_line[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            return null(await Command.send_message(execution_ctx, f"Invalid regular expression: {e}"))
        amount = len(found)
        if cmd_line[2] == '-a':
            result = str(amount)
            await Command.send_message(execution_ctx, result)
            return result
        index = await Util.parse_int(
            execution_ctx, cmd_line[2],
            f"Third parameter '{cmd_line[2]}' should be a valid index")
        if index is None:
            return None
        if not 0 <= index < amount:
            return null(await Command.send_message(
                execution_ctx, f"Wrong index in list '{cmd_line[2]}' (should be in range [0..{amount - 1}])"))
        result = found[index]
        await Command.send_message(execution_ctx, result)
        return result

    async def _dropmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        bc.markov.__init__()
        await Command.send_message(execution_ctx, "Markov database has been dropped!")

    async def _statmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show stats for Markov module
    Example: !statmarkov"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        pairs_count = sum(word.total_next for word in bc.markov.model.values())
        markov_db_size = os.path.getsize(const.MARKOV_PATH)
        while markov_db_size == 0:
            markov_db_size = os.path.getsize(const.MARKOV_PATH)
            await asyncio.sleep(1)
        if markov_db_size > 1024 * 1024:
            markov_db_size = f"{(markov_db_size / (1024 * 1024)):.2f} MB"
        else:
            markov_db_size = f"{markov_db_size / 1024:.2f} KB"
        result = (f"Markov module stats:\n"
                  f"Markov chains generated: {bc.markov.chains_generated}\n"
                  f"Words count: {len(bc.markov.model)}\n"
                  f"Pairs (word -> word) count: {pairs_count}\n"
                  f"Markov database size: {markov_db_size}\n")
        await Command.send_message(execution_ctx, result)

    async def _inspectmarkov(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Inspect next words in Markov model for current one
    Example: !inspectmarkov hello"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=3):
            return None
        word = cmd_line[1] if len(cmd_line) > 1 else ''
        words = bc.markov.get_next_words_list(word)
        result = f"Next for '{word}':\n"
        amount = len(words)
        if not ('-f' in cmd_line and
                execution_ctx.permission_level >= const.Permission.MOD.value):
            words = words[:100]
        skipped_words = amount - len(words)
        result += ', '.join([f"{word if word is not None else '<end>'}: {count}" for word, count in words])
        if skipped_words > 0:
            result += f"... and {skipped_words} more words"
        await Command.send_message(execution_ctx, result)

    async def _addmarkovfilter(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter regex"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return None
        bc.markov.filters.append(re.compile(cmd_line[1], re.DOTALL))
        await Command.send_message(execution_ctx, f"Filter '{cmd_line[1]}' was successfully added for Markov model")

    async def _listmarkovfilter(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Print list of regular expression filters for Markov model
    Example: !listmarkovfilter"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = ""
        for index, regex in enumerate(bc.markov.filters):
            result += f"{index} -> `{regex.pattern}`\n"
        await Command.send_message(execution_ctx, result or "No filters for Markov model found!")
        return result

    async def _delmarkovfilter(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete regular expression filter for Markov model by index
    Example: !delmarkovfilter 0"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1],
            f"Second parameter for '{cmd_line[0]}' should be an index of filter")
        if index is None:
            return
        if 0 <= index < len(bc.markov.filters):
            bc.markov.filters.pop(index)
            await Command.send_message(execution_ctx, "Successfully deleted filter!")
        else:
            await Command.send_message(execution_ctx, "Invalid index of filter!")

    async def _addmarkovignoredprefix(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add message prefix that should be ignored by Markov model
    Example: !addmarkovignoredprefix $"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        prefix = ' '.join(cmd_line[1:])
        index = bc.config.ids["markov_ignored_prefix"]
        bc.markov.ignored_prefixes[index] = ' '.join(cmd_line[1:])
        bc.config.ids["markov_ignored_prefix"] += 1
        await Command.send_message(execution_ctx, f"Added '{prefix}' as ignored prefix for Markov model")

    async def _listmarkovignoredprefix(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """List all prefixes that should be ignored by Markov model
    Example: !listmarkovignoredprefix"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = ""
        for index, prefix in bc.markov.ignored_prefixes.items():
            result += f"{index} -> `{prefix}`\n"
        await Command.send_message(execution_ctx, result or "No ignored prefixes for Markov model found!")

    async def _delmarkovignoredprefix(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete message prefix that should be ignored by Markov model by its index
    Example: !delmarkovignoredprefix 0"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of ignored prefix")
        if index is None:
            return
        if index in bc.markov.ignored_prefixes.keys():
            bc.markov.ignored_prefixes.pop(index)
            await Command.send_message(execution_ctx, "Successfully deleted ignored prefix!")
        else:
            await Command.send_message(execution_ctx, "Invalid index of ignored prefix!")
