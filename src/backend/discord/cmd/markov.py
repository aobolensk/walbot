"""Markov model commands"""

import functools

from src import const
from src.backend.discord.commands import bind_command
from src.commands import BaseCmd
from src.config import bc


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
            "delmarkovfilter": dict(permission=const.Permission.MOD.value, subcommand=False),
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
        self._delmarkovfilter = functools.partial(bind_command, "delmarkovfilter")
        self._addmarkovignoredprefix = functools.partial(bind_command, "addmarkovignoredprefix")
        self._listmarkovignoredprefix = functools.partial(bind_command, "listmarkovignoredprefix")
        self._delmarkovignoredprefix = functools.partial(bind_command, "delmarkovignoredprefix")
