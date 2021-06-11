import datetime
import random
from src.embed import DiscordEmbed

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.quote import Quote
from src.utils import Util, null


class QuoteCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "quote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "addquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delquote",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "setquoteauthor",
                                     permission=const.Permission.USER.value, subcommand=False)

    @staticmethod
    async def _quote(message, command, silent=False):
        """Print some quote from quotes database
    Examples:
        !quote
        !quote 1"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if not bc.config.quotes:
            return null(await Msg.response(message, "<Quotes database is empty>", silent))
        if len(command) == 2:
            index = await Util.parse_int(
                message, command[1], f"Second parameter for '{command[0]}' should be an index of quote", silent)
            if index is None:
                return
        else:
            index = random.choice(list(bc.config.quotes.keys()))
        if index not in bc.config.quotes.keys():
            return null(await Msg.response(message, "Invalid index of quote!", silent))
        quote = bc.config.quotes[index]
        e = DiscordEmbed()
        e.title("Quote")
        e.description(quote.message)
        e.color(random.randint(0x000000, 0xffffff))
        e.timestamp(datetime.datetime.strptime(str(quote.timestamp), const.TIMESTAMP_DATETIME_FORMAT))
        e.add_field("Index", str(index), True)
        e.add_field("Author", quote.author if quote.author else "<unknown>", True)
        e.add_field("Added by", quote.added_by, True)
        await Msg.response(message, "", silent, embed=e.get())

    @staticmethod
    async def _addquote(message, command, silent=False):
        """Add quote to quotes database
    Example: !addquote Hello, world!"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        quote = ' '.join(command[1:])
        index = bc.config.ids["quote"]
        bc.config.quotes[index] = Quote(quote, message.author.name)
        bc.config.ids["quote"] += 1
        await Msg.response(
            message,
            f"Quote '{quote}' was successfully added to quotes database with index {index}",
            silent)

    @staticmethod
    async def _listquote(message, command, silent=False):
        """Print list of all quotes
    Example: !listquote"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, quote in bc.config.quotes.items():
            result += f"{index} -> {quote.quote()}\n"
        if result:
            await Msg.response(message, result, silent)
        else:
            await Msg.response(message, "<Quotes database is empty>", silent)
        return result

    @staticmethod
    async def _delquote(message, command, silent=False):
        """Delete quote from quotes database by index
    Example: !delquote 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of quote", silent)
        if index is None:
            return
        if index in bc.config.quotes.keys():
            bc.config.quotes.pop(index)
            await Msg.response(message, "Successfully deleted quote!", silent)
        else:
            await Msg.response(message, "Invalid index of quote!", silent)

    @staticmethod
    async def _setquoteauthor(message, command, silent=False):
        """Set author of quote by its index
    Example: !setquoteauthor 0 WalBot"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of quote", silent)
        if index is None:
            return
        if index in bc.config.quotes.keys():
            author = ' '.join(command[2:])
            bc.config.quotes[index].author = author
            await Msg.response(
                message, f"Successfully set author '{author}' for quote '{bc.config.quotes[index].quote()}'", silent)
        else:
            await Msg.response(message, "Invalid index of quote!", silent)
