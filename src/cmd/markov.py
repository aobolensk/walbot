import re

from .. import const
from ..commands import BaseCmd
from ..config import bc
from ..utils import Util


class MarkovCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "markov",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "markovgc",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delmarkov",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "findmarkov",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "statmarkov",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "dropmarkov",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addmarkovfilter",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listmarkovfilter",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "delmarkovfilter",
                                     permission=const.Permission.MOD.value, subcommand=True)

    @staticmethod
    async def _markov(message, command, silent=False):
        """Generate message using Markov chain
    Example: !markov"""
        if not await Util.check_args_count(message, command, silent, min=1):
            return
        if len(command) > 1:
            result = ""
            for i in range(const.MAX_MARKOV_ATTEMPTS):
                result = bc.markov.generate(word=command[-1])
                if len(result.split()) > 1:
                    break
            if result != "<Empty message was generated>":
                result = ' '.join(command[1:-1]) + ' ' + result
        else:
            result = bc.markov.generate()
        result = await bc.config.disable_pings_in_response(message, result)
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _markovgc(message, command, silent=False):
        """Garbage collect Markov model nodes
    Example: !markovgc"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = bc.markov.gc()
        result = f"Garbage collected {len(result)} items: {', '.join(result)}"
        await Util.response(message, result, silent)
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
            await Util.response(message, f"Invalid regular expression: {e}", silent)
            return
        await Util.response(
            message, f"Deleted {len(removed)} words from model: {removed}", silent, suppress_embeds=True)

    @staticmethod
    async def _findmarkov(message, command, silent=False):
        """Match words in Markov model using regex
    Examples:
        !findmarkov hello
        !findmarkov hello -f"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = command[1]
        try:
            found = bc.markov.find_words(regex)
        except re.error as e:
            await Util.response(message, f"Invalid regular expression: {e}", silent)
            return
        amount = len(found)
        if not (len(command) > 2 and command[2] == '-f' and
                bc.config.users[message.author.id].permission_level >= const.Permission.MOD.value):
            found = found[:100]
        await Util.response(
            message, f"Found {amount} words in model: {found}"
                     f"{f' and {amount - len(found)} more...' if amount - len(found) > 0 else ''}",
            silent, suppress_embeds=True)

    @staticmethod
    async def _dropmarkov(message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        bc.markov.__init__()
        await Util.response(message, "Markov database has been dropped!", silent)

    @staticmethod
    async def _statmarkov(message, command, silent=False):
        """Show stats for Markov module
    Example: !statmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        pairs_count = sum(word.total_next for word in bc.markov.model.values())
        result = (f"Markov module stats:\n"
                  f"Markov chains generated: {bc.markov.chains_generated}\n"
                  f"Words count: {len(bc.markov.model)}\n"
                  f"Pairs (word -> word) count: {pairs_count}\n")
        await Util.response(message, result, silent)

    @staticmethod
    async def _addmarkovfilter(message, command, silent=False):
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter regex"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        bc.markov.filters.append(re.compile(command[1]))
        await Util.response(message, f"Filter '{command[1]}' was successfully added for Markov model", silent)

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
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No filters for Markov model found!", silent)
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
            await Util.response(message, "Successfully deleted filter!", silent)
        else:
            await Util.response(message, "Invalid index of filter!", silent)
