"""Markov model commands"""

import functools
import re

from src import const
from src.backend.discord.commands import bind_command
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
from src.utils import Util


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
        self._markov = functools.partial(bind_command, "markov")
        self._markovgc = functools.partial(bind_command, "markovgc")
        self._delmarkov = functools.partial(bind_command, "delmarkov")
        self._findmarkov = functools.partial(bind_command, "findmarkov")
        self._getmarkovword = functools.partial(bind_command, "getmarkovword")
        self._dropmarkov = functools.partial(bind_command, "dropmarkov")
        self._statmarkov = functools.partial(bind_command, "statmarkov")
        self._inspectmarkov = functools.partial(bind_command, "inspectmarkov")
        self._addmarkovfilter = functools.partial(bind_command, "addmarkovfilter")
        self._listmarkovfilter = functools.partial(bind_command, "listmarkovfilter")

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
        await Msg.response(message, result or "No ignored prefixes for Markov model found!", silent)

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
