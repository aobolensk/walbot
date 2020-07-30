import datetime

from .. import const
from ..commands import BaseCmd
from ..config import bc
from ..reminder import Reminder
from ..utils import Util


class ReminderCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.__name__, "reminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "updreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.__name__, "listreminder",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.__name__, "delreminder",
                                     permission=const.Permission.USER.value, subcommand=False)

    @staticmethod
    async def _reminder(message, command, silent=False):
        """Print message at particular time
    Example: !reminder 2020-01-01 00:00 Happy new year!"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        time = command[1] + ' ' + command[2]
        try:
            time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
        except ValueError:
            await Util.response(message, "{} does not match format {}\n"
                                "More information about format: <https://strftime.org/>".format(
                                    time, const.REMINDER_TIME_FORMAT), silent)
            return
        text = ' '.join(command[3:])
        bc.config.reminders[bc.config.ids["reminder"]] = Reminder(
            str(time), text, message.channel.id)
        bc.config.ids["reminder"] += 1
        await Util.response(message, "Reminder '{}' added at {}".format(text, time), silent)

    @staticmethod
    async def _updreminder(message, command, silent=False):
        """Update reminder by index
    Example: !updreminder 0 2020-01-01 00:00 Happy new year!"""
        if not await Util.check_args_count(message, command, silent, min=5):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of reminder"
                                     .format(command[0]), silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            time = command[2] + ' ' + command[3]
            try:
                time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
            except ValueError:
                await Util.response(message, "{} does not match format {}\n"
                                    "More information about format: <https://strftime.org/>".format(
                                        time, const.REMINDER_TIME_FORMAT), silent)
                return
            text = ' '.join(command[4:])
            bc.config.reminders[index] = Reminder(str(time), text, message.channel.id)
            await Util.response(message, "Successfully updated reminder {}: '{}' at {}".format(
                                    index, text, time), silent)
        else:
            await Util.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _listreminder(message, command, silent=False):
        """Print list of reminders
    Example: !listreminder"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        reminder_list = []
        for index, reminder in bc.config.reminders.items():
            reminder_list.append((reminder.time, "{} - {} in {} -> {}".format(
                index, reminder.time, "<#{}>".format(reminder.channel_id), reminder.message)))
        reminder_list.sort()
        result = '\n'.join([x[1] for x in reminder_list])
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reminders found!", silent)
        return result

    @staticmethod
    async def _delreminder(message, command, silent=False):
        """Delete reminder by index
    Example: !delreminder 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(message, command[1],
                                     "Second parameter for '{}' should be an index of reminder"
                                     .format(command[0]),
                                     silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            bc.config.reminders.pop(index)
            await Util.response(message, "Successfully deleted reminder!", silent)
        else:
            await Util.response(message, "Invalid index of reminder!", silent)
