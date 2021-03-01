import datetime

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.reminder import Reminder
from src.utils import Util


class ReminderCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "reminder",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "addreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "updreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listreminder",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "delreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "remindme",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "remindwme",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "repeatreminder",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "skipreminder",
                                     permission=const.Permission.USER.value, subcommand=False)

    @staticmethod
    async def _reminder(message, command, silent=False):
        """Print information about reminder
    Example:
        !reminder 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            await Msg.response(message, "Invalid index of reminder!", silent)
            return
        reminder = bc.config.reminders[index]
        result = (f"{index} - {reminder.time}"
                  f"{f' in <#{reminder.channel_id}>' if message.channel.id != reminder.channel_id else ''}"
                  f" -> {reminder.message}"
                  f"{f' (repeats every {reminder.repeat_after} minutes)' if reminder.repeat_after else ''}\n"
                  f"Author: {reminder.author}\n"
                  f"Created: {reminder.time_created}")
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _addreminder(message, command, silent=False):
        """Print message at particular time
    Examples:
        !addreminder 2020-01-01 00:00 Happy new year!
        !addreminder today 08:00 Wake up
        !addreminder tomorrow 08:00 Wake up
        !addreminder 2d 08:00 Wake up <- 2 days
        !addreminder 1w 08:00 Wake up <- 1 week
        !addreminder in 1w5d10h5m Test reminder
        !addreminder in 1w Test reminder 2
        !addreminder in 5h10m Test reminder 3
"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return

        # !listreminder in <weeks>w<days>d<hours>h<minutes>m
        if command[1] == "in":
            time = command[2]
            text = ' '.join(command[3:])
            r = const.REMINDER_IN_REGEX.match(time)
            if r is None:
                await Msg.response(
                    message, ("Provide relative time in the following format: "
                              "<weeks>w<days>d<hours>h<minutes>m. "
                              "All parts except one are optional"), silent)
            weeks = int(r.group(2)) if r.group(2) is not None else 0
            days = int(r.group(4)) if r.group(4) is not None else 0
            hours = int(r.group(6)) if r.group(6) is not None else 0
            minutes = int(r.group(8)) if r.group(8) is not None else 0
            time = (datetime.datetime.now() + datetime.timedelta(
                weeks=weeks, days=days, hours=hours, minutes=minutes)).strftime(const.REMINDER_TIME_FORMAT)
            id_ = bc.config.ids["reminder"]
            bc.config.reminders[id_] = Reminder(
                str(time), text, message.channel.id, message.author.name,
                datetime.datetime.now().strftime(const.REMINDER_TIME_FORMAT))
            bc.config.ids["reminder"] += 1
            await Msg.response(message, f"Reminder '{text}' with id {id_} added at {time}", silent)
            return

        WEEK_DAYS_FULL = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
        WEEK_DAYS_ABBREV = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

        date = command[1]
        time = command[2]
        if command[1] == "today":
            date = datetime.datetime.strftime(datetime.datetime.now(), const.REMINDER_DATE_FORMAT)
        elif command[1] == "tomorrow":
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=1), const.REMINDER_DATE_FORMAT)
        elif command[1].lower() in WEEK_DAYS_FULL or command[1] in WEEK_DAYS_ABBREV:
            if command[1].lower() in WEEK_DAYS_FULL:
                weekday = WEEK_DAYS_FULL.index(command[1].lower())
            elif command[1] in WEEK_DAYS_ABBREV:
                weekday = WEEK_DAYS_ABBREV.index(command[1].lower())
            else:
                Msg.response(message, "Unexpected error during day of week processing!", silent)
                return
            days_delta = (weekday - datetime.datetime.today().weekday() + 7) % 7
            if days_delta == 0:
                days_delta = 7
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_delta), const.REMINDER_DATE_FORMAT)
        elif command[1].endswith("d"):
            days_amount = command[1][:-1]
            days_amount = await Util.parse_int(
                message, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif command[1].endswith("w"):
            weeks_amount = command[1][:-1]
            weeks_amount = await Util.parse_int(
                message, weeks_amount, "You need to specify amount of weeks before 'w'. Example: 2w for 2 weeks",
                silent)
            if weeks_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=weeks_amount * 7), const.REMINDER_DATE_FORMAT)
        time = date + ' ' + time
        try:
            time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
        except ValueError:
            await Msg.response(message, f"{time} does not match format {const.REMINDER_TIME_FORMAT}\n"
                               "More information about format: <https://strftime.org/>", silent)
            return
        text = ' '.join(command[3:])
        id_ = bc.config.ids["reminder"]
        bc.config.reminders[id_] = Reminder(
            str(time), text, message.channel.id, message.author.name,
            datetime.datetime.now().strftime(const.REMINDER_TIME_FORMAT))
        bc.config.ids["reminder"] += 1
        await Msg.response(message, f"Reminder '{text}' with id {id_} added at {time}", silent)

    @staticmethod
    async def _updreminder(message, command, silent=False):
        """Update reminder by index
    Example: !updreminder 0 2020-01-01 00:00 Happy new year!"""
        if not await Util.check_args_count(message, command, silent, min=5):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            time = command[2] + ' ' + command[3]
            try:
                time = datetime.datetime.strptime(time, const.REMINDER_TIME_FORMAT).strftime(const.REMINDER_TIME_FORMAT)
            except ValueError:
                await Msg.response(message, f"{time} does not match format {const.REMINDER_TIME_FORMAT}\n"
                                   "More information about format: <https://strftime.org/>", silent)
                return
            text = ' '.join(command[4:])
            bc.config.reminders[index] = Reminder(
                str(time), text, message.channel.id, bc.config.reminders[index].author,
                datetime.datetime.now().strftime(const.REMINDER_TIME_FORMAT))
            await Msg.response(
                message, f"Successfully updated reminder {index}: '{text}' at {time}", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _listreminder(message, command, silent=False):
        """Print list of reminders
    Example: !listreminder"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        reminder_list = []
        for index, reminder in bc.config.reminders.items():
            reminder_list.append(
                (reminder.time,
                 f"{index} - {reminder.time}"
                 f"{f' in <#{reminder.channel_id}>' if message.channel.id != reminder.channel_id else ''}"
                 f" -> {reminder.message}"
                 f"{f' (repeats every {reminder.repeat_after} minutes)' if reminder.repeat_after else ''}"))
        reminder_list.sort()
        result = '\n'.join([x[1] for x in reminder_list])
        if result:
            await Msg.response(message, result, silent)
        else:
            await Msg.response(message, "No reminders found!", silent)
        return result

    @staticmethod
    async def _delreminder(message, command, silent=False):
        """Delete reminder by index
    Example: !delreminder 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            bc.config.reminders.pop(index)
            await Msg.response(message, "Successfully deleted reminder!", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _remindme(message, command, silent=False):
        """Ask bot to ping you when it sends reminder
    Example: !remindme 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            bc.config.reminders[index].ping_users.append(message.author.mention)
            await Msg.response(message, f"You will be mentioned when reminder {index} is sent", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _remindwme(message, command, silent=False):
        """Ask bot to send direct message you when it sends reminder
    Example: !remindwme 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            bc.config.reminders[index].whisper_users.append(message.author.id)
            await Msg.response(
                message, f"You will be notified in direct messages when reminder {index} is sent", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _repeatreminder(message, command, silent=False):
        """Make reminder repeating with particular period
    Examples:
        !repeatreminder 1 1
        !repeatreminder 1 1h
        !repeatreminder 1 1d
        !repeatreminder 1 1w
    Note: number without postfix is translated to minutes"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            await Msg.response(message, "Invalid index of reminder!", silent)
            return
        if command[2].endswith("h"):
            duration = command[2][:-1]
            duration = await Util.parse_int(
                message, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if duration is None:
                return
            duration *= 60
        elif command[2].endswith("d"):
            duration = command[2][:-1]
            duration = await Util.parse_int(
                message, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if duration is None:
                return
            duration *= 1440
        elif command[2].endswith("w"):
            duration = command[2][:-1]
            duration = await Util.parse_int(
                message, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if duration is None:
                return
            duration *= 10080
        else:
            duration = await Util.parse_int(
                message, command[2],
                f"Third parameter for '{command[0]}' should be duration of period between reminders", silent)
            if duration is None:
                return
        if duration == 0:
            await Msg.response(message, f"Repetition is disabled for reminder {index}", silent)
            return
        if duration < 0:
            await Msg.response(message, "Duration should be positive or zero (to disable repetition)!", silent)
            return
        bc.config.reminders[index].repeat_after = duration
        await Msg.response(message, f"Reminder {index} will be repeated every {duration} minutes!", silent)

    @staticmethod
    async def _skipreminder(message, command, silent=False):
        """Skip next instance of recurring (repeating) reminder
    Example: !skipreminder 1
    Note: only recurring (repeating) reminders are affected by this command"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            await Msg.response(message, "Invalid index of reminder!", silent)
            return
        if bc.config.reminders[index].repeat_after == 0:
            await Msg.response(message, "This reminder is not recurring!", silent)
            return
        rem = bc.config.reminders[index]
        new_time = datetime.datetime.strftime(
            datetime.datetime.strptime(rem.time, const.REMINDER_TIME_FORMAT) +
            datetime.timedelta(minutes=rem.repeat_after), const.REMINDER_TIME_FORMAT)
        id_ = bc.config.ids["reminder"]
        bc.config.reminders[id_] = Reminder(
            str(new_time), rem.message, message.channel.id, bc.config.reminders[id_].author,
            datetime.datetime.now().strftime(const.REMINDER_TIME_FORMAT))
        bc.config.reminders[id_].repeat_after = rem.repeat_after
        bc.config.ids["reminder"] += 1
        bc.config.reminders.pop(index)
        await Msg.response(
            message, f"Skipped reminder {index} at {rem.time}, "
                     f"next reminder {id_} will be at {bc.config.reminders[id_].time}", silent)
