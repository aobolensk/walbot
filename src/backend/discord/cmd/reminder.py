"""WalBot reminders"""

from src import const
from src.backend.discord.context import DiscordExecutionContext
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

    @staticmethod
    async def _reminder(message, command, silent=False):
        return bc.executor.commands["reminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _addreminder(message, command, silent=False):
        return bc.executor.commands["addreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _updreminder(message, command, silent=False):
        return bc.executor.commands["updreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _listreminder(message, command, silent=False):
        return bc.executor.commands["listreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _delreminder(message, command, silent=False):
        return bc.executor.commands["delreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindme(message, command, silent=False):
        return bc.executor.commands["remindme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindwme(message, command, silent=False):
        return bc.executor.commands["remindwme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindeme(message, command, silent=False):
        return bc.executor.commands["remindeme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _repeatreminder(message, command, silent=False):
        return bc.executor.commands["repeatreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _skipreminder(message, command, silent=False):
        return bc.executor.commands["skipreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _timeuntilreminder(message, command, silent=False):
        return bc.executor.commands["timeuntilreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _setprereminders(message, command, silent=False):
        return bc.executor.commands["setprereminders"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _addremindernotes(message, command, silent=False):
        return bc.executor.commands["addremindernotes"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _setreminderchannel(message, command, silent=False):
        return bc.executor.commands["setreminderchannel"].run(command, DiscordExecutionContext(message, silent))
