import re

from .. import const
from ..commands import BaseCmd
from ..config import bc
from ..utils import Util


class MarkovCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.__name__, "markov",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__name__, "markovgc",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "delmarkov",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "findmarkov",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "dropmarkov",
                                     permission=const.Permission.ADMIN.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "addmarkovfilter",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "listmarkovfilter",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__name__, "delmarkovfilter",
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
                if len(result.split()) > len(command) - 1:
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
        result = "Garbage collected {} items: {}".format(len(result), ', '.join(result))
        await Util.response(message, result, silent)
        return result

    @staticmethod
    async def _delmarkov(message, command, silent=False):
        """Delete all words in Markov model by regex
    Example: !delmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        removed = bc.markov.del_words(regex)
        await Util.response(message, "Deleted {} words from model: {}".format(str(len(removed)),
                            str(removed)), silent, suppress_embeds=True)

    @staticmethod
    async def _findmarkov(message, command, silent=False):
        """Match words in Markov model using regex
    Example: !findmarkov hello"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        regex = ' '.join(command[1:])
        found = bc.markov.find_words(regex)
        await Util.response(message, "Found {} words in model: {}".format(str(len(found)),
                            str(found)), silent, suppress_embeds=True)

    @staticmethod
    async def _dropmarkov(message, command, silent=False):
        """Drop Markov database
    Example: !dropmarkov"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        bc.markov.__init__()
        await Util.response(message, "Markov database has been dropped!", silent)

    @staticmethod
    async def _addmarkovfilter(message, command, silent=False):
        """Add regular expression filter for Markov model
    Example: !addmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        bc.markov.filters.append(re.compile(command[1]))
        await Util.response(message, "Filter '{}' was successfully added for Markov model".format(command[1]), silent)

    @staticmethod
    async def _listmarkovfilter(message, command, silent=False):
        """Print list of regular expression filters for Markov model
    Example: !listmarkovfilter"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, regex in enumerate(bc.markov.filters):
            result += "{} -> {}\n".format(index, regex.pattern)
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
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of filter"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if 0 <= index < len(bc.markov.filters):
            bc.markov.filters.pop(index)
            await Util.response(message, "Successfully deleted filter!", silent)
        else:
            await Util.response(message, "Invalid index of filter!", silent)
