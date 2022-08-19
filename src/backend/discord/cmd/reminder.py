"""WalBot reminders"""

from src import const
from src.backend.discord.context import DiscordExecutionContext
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
from src.utils import Util, null


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
        """Print information about reminder
    Example:
        !reminder 1"""
        return bc.executor.commands["reminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _addreminder(message, command, silent=False):
        """Print message at particular time
    Examples:
        !addreminder 2020-01-01 00:00 Happy new year!
        !addreminder today 08:00 Wake up
        !addreminder tomorrow 08:00 Wake up
        !addreminder monday 09:00 Time to work
        !addreminder sat 11:00 Time to chill
        !addreminder 2d 08:00 Wake up <- 2 days
        !addreminder 1w 08:00 Wake up <- 1 week
        !addreminder 1m Monthly event
        !addreminder 1y Annual event
        !addreminder in 1w5d10h5m Test reminder
        !addreminder in 1w Test reminder 2
        !addreminder in 5h10m Test reminder 3
"""
        return bc.executor.commands["addreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _updreminder(message, command, silent=False):
        """Update reminder by index
    Examples:
        !updreminder 0 2020-01-01 00:00 Happy new year!
        !updreminder 0 2020-01-01 00:00 Happy new year!
        !updreminder 0 today 08:00 Wake up
        !updreminder 0 tomorrow 08:00 Wake up
        !updreminder 0 monday 09:00 Time to work
        !updreminder 0 sat 11:00 Time to chill
        !updreminder 0 2d 08:00 Wake up <- 2 days
        !updreminder 0 1w 08:00 Wake up <- 1 week
        !addreminder 0 1m Monthly event
        !addreminder 0 1y Annual event
        !updreminder 0 in 1w5d10h5m Test reminder
        !updreminder 0 in 1w Test reminder 2
        !updreminder 0 in 5h10m Test reminder 3
"""
        return bc.executor.commands["updreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _listreminder(message, command, silent=False):
        """Print list of reminders
    Examples:
        !listreminder
        !listreminder 5 <- prints only first 5 reminders"""
        return bc.executor.commands["listreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _delreminder(message, command, silent=False):
        """Delete reminders by index
    Example: !delreminder 0 1 2"""
        return bc.executor.commands["delreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindme(message, command, silent=False):
        """Ask bot to ping you when it sends reminder
    Example: !remindme 1"""
        return bc.executor.commands["remindme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindwme(message, command, silent=False):
        """Ask bot to send direct message you when it sends reminder
    Example: !remindwme 1"""
        return bc.executor.commands["remindwme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _remindeme(message, command, silent=False):
        """Ask bot to send you an e-mail when it sends reminder
    Example: !remindeme 1 <your-email-address>"""
        return bc.executor.commands["remindeme"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _repeatreminder(message, command, silent=False):
        """Make reminder repeating with particular period
    Examples:
        !repeatreminder 1 1
        !repeatreminder 1 hourly
        !repeatreminder 1 daily
        !repeatreminder 1 weekly
        !repeatreminder 1 monthly
        !repeatreminder 1 annually
        !repeatreminder 1 2h
        !repeatreminder 1 2d
        !repeatreminder 1 2w
        !repeatreminder 1 2m
        !repeatreminder 1 2y
        !repeatreminder 1 0
    Note: number without postfix is translated to minutes. 0 means disabling repetition"""
        return bc.executor.commands["repeatreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _skipreminder(message, command, silent=False):
        """Skip next instance of recurring (repeating) reminder
    Example: !skipreminder 1
    Note: only recurring (repeating) reminders are affected by this command"""
        return bc.executor.commands["skipreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _timeuntilreminder(message, command, silent=False):
        """Show time until particular reminder
    Example: !timeuntilreminder 1"""
        return bc.executor.commands["timeuntilreminder"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _setprereminders(message, command, silent=False):
        """Set pre reminders notifying that reminder will be sent in particular time.
        For example, send pre reminder 10 minutes before actual event (to prepare or something)
    Usage: !setprereminders <reminder_id> [<time_before_reminder_in_minutes> ...]
    Examples:
        !setprereminders 1 10
        !setprereminders 2 5 10 15"""
        return bc.executor.commands["setprereminders"].run(command, DiscordExecutionContext(message, silent))

    @staticmethod
    async def _addremindernotes(message, command, silent=False):
        """Add reminder notes
    Example: !addremindernotes 1 Some text"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        rem = bc.config.reminders[index]
        rem.notes = ' '.join(command[2:])
        await Msg.response(message, f"Set notes for reminder {index}: {rem.notes}", silent)

    @staticmethod
    async def _setreminderchannel(message, command, silent=False):
        """Set channel where reminder will be sent
    Example: !setreminderchannel 1 <channel_id>"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        rem = bc.config.reminders[index]
        channel_id = await Util.parse_int(
            message, command[2], f"Third parameter for '{command[0]}' should be channel id", silent)
        if channel_id is None:
            return
        rem.channel_id = channel_id
        await Msg.response(message, f"Set channel id {channel_id} for reminder {index}", silent)
