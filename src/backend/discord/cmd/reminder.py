"""WalBot reminders"""

import functools

from src import const
from src.backend.discord.commands import bind_command
from src.commands import BaseCmd
from src.config import bc


class ReminderCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "reminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "addreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "updreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "listreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "delreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "remindme": dict(permission=const.Permission.USER.value, subcommand=False),
            "remindwme": dict(permission=const.Permission.USER.value, subcommand=False),
            "remindeme": dict(permission=const.Permission.MOD.value, subcommand=False),
            "repeatreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "skipreminder": dict(permission=const.Permission.USER.value, subcommand=False),
            "timeuntilreminder": dict(permission=const.Permission.USER.value, subcommand=True),
            "setprereminders": dict(permission=const.Permission.USER.value, subcommand=False),
            "addremindernotes": dict(permission=const.Permission.USER.value, subcommand=False),
            "setreminderchannel": dict(permission=const.Permission.USER.value, subcommand=False),
        })
        self._reminder = functools.partial(bind_command, "reminder")
        self._addreminder = functools.partial(bind_command, "addreminder")
        self._updreminder = functools.partial(bind_command, "updreminder")
        self._listreminder = functools.partial(bind_command, "listreminder")
        self._delreminder = functools.partial(bind_command, "delreminder")
        self._remindme = functools.partial(bind_command, "remindme")
        self._remindwme = functools.partial(bind_command, "remindwme")
        self._remindeme = functools.partial(bind_command, "remindeme")
        self._repeatreminder = functools.partial(bind_command, "repeatreminder")
        self._skipreminder = functools.partial(bind_command, "skipreminder")
        self._timeuntilreminder = functools.partial(bind_command, "timeuntilreminder")
        self._setprereminders = functools.partial(bind_command, "setprereminders")
        self._addremindernotes = functools.partial(bind_command, "addremindernotes")
        self._setreminderchannel = functools.partial(bind_command, "setreminderchannel")
