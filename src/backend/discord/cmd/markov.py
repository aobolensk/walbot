"""Markov model commands"""

import asyncio
import os
import re

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.utils import Util, null


class MarkovCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "markov": dict(permission=const.Permission.USER.value, subcommand=True),
            "markovgc": dict(permission=const.Permission.USER.value, subcommand=False),
            "delmarkov": dict(permission=const.Permission.MOD.value, subcommand=False),
            "findmarkov": dict(permission=const.Permission.USER.value, subcommand=False),
            "getmarkovword": dict(permission=const.Permission.USER.value, subcommand=True),
            "statmarkov": dict(permission=const.Permission.USER.value, subcommand=False),
            "dropmarkov": dict(permission=const.Permission.ADMIN.value, subcommand=False),
            "inspectmarkov": dict(permission=const.Permission.USER.value, subcommand=False),
            "addmarkovfilter": dict(permission=const.Permission.MOD.value, subcommand=False),
            "listmarkovfilter": dict(permission=const.Permission.USER.value, subcommand=True),
            "delmarkovfilter": dict(permission=const.Permission.MOD.value, subcommand=True),
            "addmarkovignoredprefix": dict(permission=const.Permission.MOD.value, subcommand=True),
            "listmarkovignoredprefix": dict(permission=const.Permission.MOD.value, subcommand=True),
            "delmarkovignoredprefix": dict(permission=const.Permission.MOD.value, subcommand=True),
        })

    @staticmethod
    async def _markov(message, command, silent=False):
        """Generate message using Markov chain
    Example: !markov"""
        if not await Util.check_args_count(message, command, silent, min=1):
            return
        if len(command) > 1:
            result = ""
            for _ in range(const.MAX_MARKOV_ATTEMPTS):
                result = bc.markov.generate(word=command[-1])
                if len(result.split()) > 1:
                    break
            if result != "<Empty message was generated>":
                result = ' '.join(command[1:-1]) + ' ' + result
        else:
            result = bc.markov.generate()
        result = await bc.config.disable_pings_in_response(message, result)
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _markovgc(message, command, silent=False):
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.markov.collect_garbage()
        result = f"Garbage collected {len(result)} items: {', '.join(result)}"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _delmarkov(message, command, silent=False):
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        try:
            removed = bc.markov.del_words(regex)
        except re.error as e:
            return null(await Msg.response(message, f"Invalid regular expression: {e}", silent))
        await Msg.response(
            message, f"Deleted {len(removed)} words from model: {removed}", silent, suppress_embeds=True)

    @staticmethod
    async def _findmarkov(message, command, silent=False):
        """Match words in Markov model using regex
    Examples:
        !findmarkov hello
        !findmarkov hello -f"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        regex = command[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            return null(await Msg.response(message, f"Invalid regular expression: {e}", silent))
        amount = len(found)
        if not (len(command) > 2 and command[2] == '-f' and
                bc.config.users[message.author.id].permission_level >= const.Permission.MOD.value):
            found = found[:100]
        await Msg.response(
            message, f"Found {amount} words in model: {found}"
                     f"{f' and {amount - len(found)} more...' if amount - len(found) > 0 else ''}",
            silent, suppress_embeds=True)

    @staticmethod
    async def _getmarkovword(message, command, silent=False):
        """Get particular word from Markov model by regex
    Examples:
        !getmarkovword hello -a <- get amount of found words
        !getmarkovword hello 0 <- get word by index"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        regex = command[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            return null(await Msg.response(message, f"Invalid regular expression: {e}", silent))
        amount = len(found)
        if command[2] == '-a':
            result = str(amount)
            await Msg.response(message, result, silent)
            return result
        index = await Util.parse_int(
            message, command[2],
            f"Third parameter '{command[2]}' should be a valid index", silent)
        if index is None:
            return
        if not 0 <= index < amount:
            return null(
                await Msg.response(
                    message,
                    f"Wrong index in list '{command[2]}' (should be in range [0..{amount-1}])",
                    silent))
        result = found[index]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _dropmarkov(message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        bc.markov.__init__()
        await Msg.response(message, "Markov database has been dropped!", silent)

    @staticmethod
    async def _statmarkov(message, command, silent=False):
        """Show stats for Markov module
    Example: !statmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
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
        await Msg.response(message, result, silent)

    @staticmethod
    async def _inspectmarkov(message, command, silent=False):
        """Inspect next words in Markov model for current one
    Example: !inspectmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=1, max=3):
            return
        word = command[1] if len(command) > 1 else ''
        words = bc.markov.get_next_words_list(word)
        result = f"Next for '{word}':\n"
        amount = len(words)
        if not ('-f' in command and
                bc.config.users[message.author.id].permission_level >= const.Permission.MOD.value):
            words = words[:100]
        skipped_words = amount - len(words)
        result += ', '.join([f"{word if word is not None else '<end>'}: {count}" for word, count in words])
        if skipped_words > 0:
            result += f"... and {skipped_words} more words"
        await Msg.response(message, result, silent, suppress_embeds=True)

    @staticmethod
    async def _addmarkovfilter(message, command, silent=False):
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter regex"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        bc.markov.filters.append(re.compile(command[1], re.DOTALL))
        await Msg.response(message, f"Filter '{command[1]}' was successfully added for Markov model", silent)

    @staticmethod
    async def _listmarkovfilter(message, command, silent=False):
        """Print list of regular expression filters for Markov model
    Example: !listmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, regex in enumerate(bc.markov.filters):
            result += f"{index} -> `{regex.pattern}`\n"
        if result:
            await Msg.response(message, result, silent)
        else:
            await Msg.response(message, "No filters for Markov model found!", silent)
        return result

    @staticmethod
    async def _delmarkovfilter(message, command, silent=False):
        """Delete regular expression filter for Markov model by index
    Example: !delmarkovfilter 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of filter", silent)
        if index is None:
            return
        if 0 <= index < len(bc.markov.filters):
            bc.markov.filters.pop(index)
            await Msg.response(message, "Successfully deleted filter!", silent)
        else:
            await Msg.response(message, "Invalid index of filter!", silent)

    @staticmethod
    async def _addmarkovignoredprefix(message, command, silent=False):
        """Add message prefix that should be ignored by Markov model
    Example: !addmarkovignoredprefix $"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        prefix = ' '.join(command[1:])
        index = bc.config.ids["markov_ignored_prefix"]
        bc.markov.ignored_prefixes[index] = ' '.join(command[1:])
        bc.config.ids["markov_ignored_prefix"] += 1
        await Msg.response(message, f"Added '{prefix}' as ignored prefix for Markov model", silent)

    @staticmethod
    async def _listmarkovignoredprefix(message, command, silent=False):
        """List all prefixes that should be ignored by Markov model
    Example: !listmarkovignoredprefix"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, prefix in bc.markov.ignored_prefixes.items():
            result += f"{index} -> `{prefix}`\n"
        if result:
            await Msg.response(message, result, silent)
        else:
            await Msg.response(message, "No ignored prefixes for Markov model found!", silent)

    @staticmethod
    async def _delmarkovignoredprefix(message, command, silent=False):
        """Delete message prefix that should be ignored by Markov model by its index
    Example: !delquote 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of ignored prefix", silent)
        if index is None:
            return
        if index in bc.markov.ignored_prefixes.keys():
            bc.markov.ignored_prefixes.pop(index)
            await Msg.response(message, "Successfully deleted ignored prefix!", silent)
        else:
            await Msg.response(message, "Invalid index of ignored prefix!", silent)