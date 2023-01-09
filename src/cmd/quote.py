"""Interaction with WalBot quote database"""

import datetime
import random
from typing import List

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.api.quote import Quote
from src.backend.discord.embed import DiscordEmbed
from src.config import bc
from src.utils import Util


class RandomCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self):
        bc.executor.commands["quote"] = Command(
            "quote", "quote", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._quote)
        bc.executor.commands["addquote"] = Command(
            "quote", "addquote", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addquote)
        bc.executor.commands["listquote"] = Command(
            "quote", "listquote", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listquote)
        bc.executor.commands["delquote"] = Command(
            "quote", "delquote", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delquote)
        bc.executor.commands["setquoteauthor"] = Command(
            "quote", "setquoteauthor", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setquoteauthor)

    async def _quote(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print some quote from quotes database
    Examples:
        !quote
        !quote 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if not bc.config.quotes:
            return await Command.send_message(execution_ctx, "<Quotes database is empty>")
        if len(cmd_line) == 2:
            index = await Util.parse_int(
                execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of quote")
            if index is None:
                return
        else:
            index = random.choice(list(bc.config.quotes.keys()))
        if index not in bc.config.quotes.keys():
            return await Command.send_message(execution_ctx, "Invalid index of quote!")
        quote = bc.config.quotes[index]
        if execution_ctx.platform == const.BotBackend.DISCORD:
            e = DiscordEmbed()
            e.title("Quote")
            e.description(quote.message)
            e.color(random.randint(0x000000, 0xffffff))
            e.timestamp(datetime.datetime.strptime(str(quote.timestamp), const.TIMESTAMP_DATETIME_FORMAT))
            e.add_field("Index", str(index), True)
            e.add_field("Author", quote.author if quote.author else "<unknown>", True)
            e.add_field("Added by", quote.added_by, True)
            await Command.send_message(execution_ctx, None, embed=e.get())
        else:
            await Command.send_message(execution_ctx, f"Quote {index}: {bc.config.quotes[index].full_quote()}")

    async def _addquote(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add quote to quotes database
    Example: !addquote Hello, world!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        quote = ' '.join(cmd_line[1:])
        index = bc.config.ids["quote"]
        bc.config.quotes[index] = Quote(quote, execution_ctx.message_author())
        bc.config.ids["quote"] += 1
        await Command.send_message(
            execution_ctx, f"Quote '{quote}' was successfully added to quotes database with index {index}")

    async def _listquote(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of all quotes
    Example: !listquote"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        result = ""
        for index, quote in bc.config.quotes.items():
            result += f"{index} -> {quote.quote()}\n"
        await Command.send_message(execution_ctx, result or "<Quotes database is empty>")
        return result

    async def _delquote(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete quote from quotes database by index
    Example: !delquote 0"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of quote")
        if index is None:
            return
        if index in bc.config.quotes.keys():
            bc.config.quotes.pop(index)
            await Command.send_message(execution_ctx, f"Successfully deleted quote {index}!")
        else:
            await Command.send_message(execution_ctx, "Invalid index of quote!")

    async def _setquoteauthor(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set author of quote by its index
    Example: !setquoteauthor 0 WalBot"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of quote")
        if index is None:
            return
        if index in bc.config.quotes.keys():
            author = ' '.join(cmd_line[2:])
            bc.config.quotes[index].author = author
            await Command.send_message(
                execution_ctx, f"Successfully set author '{author}' for quote '{bc.config.quotes[index].quote()}'")
        else:
            await Command.send_message(execution_ctx, "Invalid index of quote!")
