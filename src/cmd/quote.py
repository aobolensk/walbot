import random

from .. import const
from ..commands import BaseCmd
from ..config import bc
from ..quote import Quote
from ..utils import Util


class QuoteCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, "QuoteCommands", "quote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, "QuoteCommands", "addquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, "QuoteCommands", "listquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, "QuoteCommands", "delquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, "QuoteCommands", "setquoteauthor",
                                     permission=const.Permission.USER.value, subcommand=False)

    @staticmethod
    async def _quote(message, command, silent=False):
        """Print some quote from quotes database
    Examples:
        !quote
        !quote 1"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if not bc.commands.config.quotes:
            await Util.response(message, "<Quotes database is empty>", silent)
            return
        if len(command) == 2:
            index = await Util.parse_int(message, command[1],
                                         "Second parameter for '{}' should be an index of quote"
                                         .format(command[0]),
                                         silent)
            if index is None:
                return
        else:
            index = random.randint(0, len(bc.commands.config.quotes) - 1)
        if 0 <= index < len(bc.commands.config.quotes):
            await Util.response(message,
                                "Quote {}: {}".format(index, bc.commands.config.quotes[index].full_quote()), silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)

    @staticmethod
    async def _addquote(message, command, silent=False):
        """Add quote to quotes database
    Example: !addquote Hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        quote = ' '.join(command[1:])
        bc.commands.config.quotes.append(Quote(quote, str(message.author)))
        await Util.response(message,
                            "Quote '{}' was successfully added to quotes database with index {}".format(
                                quote, len(bc.commands.config.quotes) - 1), silent)

    @staticmethod
    async def _listquote(message, command, silent=False):
        """Print list of all quotes
    Example: !listquote"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, quote in enumerate(bc.commands.config.quotes):
            result += "{} -> {}\n".format(index, quote.quote())
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "<Quotes database is empty>", silent)
        return result

    @staticmethod
    async def _delquote(message, command, silent=False):
        """Delete quote from quotes database by index
    Example: !delquote 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of quote"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if 0 <= index < len(bc.commands.config.quotes):
            bc.commands.config.quotes.pop(index)
            await Util.response(message, "Successfully deleted quote!", silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)

    @staticmethod
    async def _setquoteauthor(message, command, silent=False):
        """Set author of quote by its index
    Example: !setquoteauthor 0 WalBot"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of quote"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if 0 <= index < len(bc.commands.config.quotes):
            author = ' '.join(command[2:])
            bc.commands.config.quotes[index].author = author
            await Util.response(message,
                                "Successfully set author '{}' for quote '{}'".format(
                                    author, bc.commands.config.quotes[index].quote()), silent)
        else:
            await Util.response(message, "Invalid index of quote!", silent)
