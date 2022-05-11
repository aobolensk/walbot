"""WalBot reminders"""

import datetime
import random

import dateutil.relativedelta

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.embed import DiscordEmbed
from src.message import Msg
from src.reminder import Reminder
from src.utils import Util, null


class _ReminderInternals:
    @staticmethod
    async def parse_reminder_args(message, date, time, silent):
        WEEK_DAYS_FULL = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
        WEEK_DAYS_ABBREV = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

        if date == "today":
            date = datetime.datetime.strftime(datetime.datetime.now(), const.REMINDER_DATE_FORMAT)
        elif date == "tomorrow":
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=1), const.REMINDER_DATE_FORMAT)
        elif date.lower() in WEEK_DAYS_FULL or date in WEEK_DAYS_ABBREV:
            if date.lower() in WEEK_DAYS_FULL:
                weekday = WEEK_DAYS_FULL.index(date.lower())
            elif date in WEEK_DAYS_ABBREV:
                weekday = WEEK_DAYS_ABBREV.index(date.lower())
            else:
                return null(await Msg.response(message, "Unexpected error during day of week processing!", silent))
            days_delta = (weekday - datetime.datetime.today().weekday() + 7) % 7
            if days_delta == 0:
                days_delta = 7
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_delta), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = await Util.parse_int(
                message, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = await Util.parse_int(
                message, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days", silent)
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("w"):
            weeks_amount = date[:-1]
            weeks_amount = await Util.parse_int(
                message, weeks_amount, "You need to specify amount of weeks before 'w'. Example: 2w for 2 weeks",
                silent)
            if weeks_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=weeks_amount * 7), const.REMINDER_DATE_FORMAT)
        elif date.endswith("m"):
            months_amount = date[:-1]
            months_amount = await Util.parse_int(
                message, months_amount,
                "You need to specify amount of months before 'm'. Example: 3m for 3 months", silent)
            if months_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() +
                dateutil.relativedelta.relativedelta(months=months_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("y"):
            years_amount = date[:-1]
            years_amount = await Util.parse_int(
                message, years_amount,
                "You need to specify amount of years before 'y'. Example: 3y for 3 years", silent)
            if years_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() +
                dateutil.relativedelta.relativedelta(years=years_amount), const.REMINDER_DATE_FORMAT)
        time = date + ' ' + time
        try:
            time = datetime.datetime.strptime(
                time, const.REMINDER_DATETIME_FORMAT).strftime(const.REMINDER_DATETIME_FORMAT)
        except ValueError:
            return null(
                await Msg.response(
                    message,
                    f"{time} does not match format {const.REMINDER_DATETIME_FORMAT}\n"
                    "More information about format: <https://strftime.org/>", silent))
        return time

    @staticmethod
    async def parse_reminder_args_in(message, time, silent):
        r = const.REMINDER_IN_REGEX.match(time)
        if r is None:
            return null(
                await Msg.response(
                    message, ("Provide relative time in the following format: "
                              "<weeks>w<days>d<hours>h<minutes>m. "
                              "All parts except one are optional"), silent))
        weeks = int(r.group(2)) if r.group(2) is not None else 0
        days = int(r.group(4)) if r.group(4) is not None else 0
        hours = int(r.group(6)) if r.group(6) is not None else 0
        minutes = int(r.group(8)) if r.group(8) is not None else 0
        time = (datetime.datetime.now() + datetime.timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes)).strftime(const.REMINDER_DATETIME_FORMAT)
        return time


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
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        reminder = bc.config.reminders[index]
        e = DiscordEmbed()
        e.title("Reminder info")
        e.description(reminder.message)
        e.footer(f"{reminder.author} • {datetime.datetime.strptime(reminder.time, const.REMINDER_DATETIME_FORMAT)}")
        e.add_field("Index", str(index), True)
        e.add_field("Channel", f"<#{reminder.channel_id}>", True)
        if reminder.repeat_after:
            e.add_field("Repeats every", f"{reminder.repeat_after} {reminder.repeat_interval_measure}", True)
        e.add_field("Created", reminder.time_created, True)
        if reminder.prereminders_list:
            e.add_field("Pre reminders (in minutes)", ', '.join([str(x) for x in reminder.prereminders_list]), True)
        if reminder.notes:
            e.add_field("Notes", reminder.notes, True)
        await Msg.response(message, None, silent, embed=e.get())

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
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        text = ' '.join(command[3:])
        if command[1] == "in":
            time = await _ReminderInternals.parse_reminder_args_in(message, command[2], silent)
        else:
            time = await _ReminderInternals.parse_reminder_args(message, command[1], command[2], silent)
        if time is None:
            return
        id_ = bc.config.ids["reminder"]
        if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
            return null(await Msg.response(message, "Reminder timestamp is earlier than now", silent))
        bc.config.reminders[id_] = Reminder(
            str(time), text, message.channel.id, message.author.name,
            datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT))
        bc.config.ids["reminder"] += 1
        await Msg.response(message, f"Reminder '{text}' with id {id_} added at {time}", silent)

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
        if not await Util.check_args_count(message, command, silent, min=5):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index in bc.config.reminders.keys():
            text = ' '.join(command[4:])
            if command[2] == "in":
                time = await _ReminderInternals.parse_reminder_args_in(message, command[3], silent)
            else:
                time = await _ReminderInternals.parse_reminder_args(message, command[2], command[3], silent)
            if time is None:
                return
            if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
                return null(await Msg.response(message, "Reminder timestamp is earlier than now", silent))
            bc.config.reminders[index] = Reminder(
                str(time), text, message.channel.id, bc.config.reminders[index].author,
                datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT))
            await Msg.response(
                message, f"Successfully updated reminder {index}: '{text}' at {time}", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

    @staticmethod
    async def _listreminder(message, command, silent=False):
        """Print list of reminders
    Examples:
        !listreminder
        !listreminder 5 <- prints only first 5 reminders"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 2:
            count = await Util.parse_int(
                message, command[1],
                f"Second parameter for '{command[0]}' should be amount of reminders to print", silent)
            if count is None:
                return
            reminders_count = count
        else:
            reminders_count = len(bc.config.reminders)
        reminder_list = []
        for index, reminder in bc.config.reminders.items():
            rep = f' (repeats every {reminder.repeat_after} {reminder.repeat_interval_measure})'
            prereminders = f' ({", ".join([str(x) + " min" for x in reminder.prereminders_list])} prereminders enabled)'
            notes = "Notes: " + Util.cut_string(reminder.notes, 200) + "\n"
            reminder_list.append(
                (reminder.time,
                 Util.cut_string(reminder.message, 256),
                 f"{notes if reminder.notes else ''}"
                 f"{index} at {reminder.time} "
                 f"{f' in <#{reminder.channel_id}>' if message.channel.id != reminder.channel_id else ''}"
                 f"{rep if reminder.repeat_after else ''}"
                 f"{prereminders if reminder.prereminders_list else ''}"))
        reminder_list.sort()
        reminder_list = reminder_list[:reminders_count]
        embed_color = random.randint(0x000000, 0xffffff)
        for reminder_chunk in Msg.split_by_chunks(reminder_list, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
            e = DiscordEmbed()
            e.title("List of reminders")
            e.color(embed_color)
            for rem in reminder_chunk:
                e.add_field(rem[1], rem[2])
            await Msg.response(message, None, silent, embed=e.get())

    @staticmethod
    async def _delreminder(message, command, silent=False):
        """Delete reminders by index
    Example: !delreminder 0 1 2"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        errors = []
        passed = []
        for i in range(1, len(command)):
            index = await Util.parse_int(
                message, command[i], f"Parameters for '{command[0]}' should be indexes of reminder", silent)
            if index is None:
                return
            if index in bc.config.reminders.keys():
                passed.append(command[i])
                bc.config.reminders.pop(index)
            else:
                errors.append(command[i])
        outstr = ""
        if len(passed):
            if len(passed) > 1:
                outstr += "Successfully deleted reminders #"
            else:
                outstr += "Successfully deleted reminder #"
            outstr += ', '.join(map(str, passed)) + '\n'
        if len(errors):
            if len(errors) > 1:
                outstr += "Invalid reminder indexes: "
            else:
                outstr += "Invalid reminder index: "
            outstr += ', '.join(map(str, errors))
        await Msg.response(message, outstr, silent)

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
    async def _remindeme(message, command, silent=False):
        """Ask bot to send you an e-mail when it sends reminder
    Example: !remindeme 1 <your-email-address>"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        email = command[2]
        if index in bc.config.reminders.keys():
            bc.config.reminders[index].email_users.append(email)
            await Msg.response(message, f"E-mail will be sent to you when reminder {index} is sent", silent)
        else:
            await Msg.response(message, "Invalid index of reminder!", silent)

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
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))

        if command[2] == "hourly":
            command[2] = "1h"
        elif command[2] == "daily":
            command[2] = "1d"
        elif command[2] == "weekly":
            command[2] = "1w"
        elif command[2] == "monthly":
            command[2] = "1m"
        elif command[2] == "annually":
            command[2] = "1y"

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
        elif command[2].endswith("m"):
            duration = command[2][:-1]
            duration = await Util.parse_int(
                message, duration, "You need to specify amount of days before 'm'. Example: 3m for 3 months", silent)
            if duration is None:
                return
            bc.config.reminders[index].repeat_interval_measure = "months"
        elif command[2].endswith("y"):
            duration = command[2][:-1]
            duration = await Util.parse_int(
                message, duration, "You need to specify amount of days before 'y'. Example: 3y for 3 years", silent)
            if duration is None:
                return
            bc.config.reminders[index].repeat_interval_measure = "years"
        else:
            duration = await Util.parse_int(
                message, command[2],
                f"Third parameter for '{command[0]}' should be duration of period between reminders", silent)
            if duration is None:
                return
        if duration < 0:
            return null(
                await Msg.response(message, "Duration should be positive or zero (to disable repetition)!", silent))
        bc.config.reminders[index].repeat_after = duration
        if duration == 0:
            return null(await Msg.response(message, f"Repetition is disabled for reminder {index}", silent))
        await Msg.response(
            message,
            f"Reminder {index} will be repeated every {duration} "
            f"{bc.config.reminders[index].repeat_interval_measure}!", silent)

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
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        if bc.config.reminders[index].repeat_after == 0:
            return null(await Msg.response(message, "This reminder is not recurring!", silent))
        rem = bc.config.reminders[index]
        new_time = datetime.datetime.strftime(
            datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) +
            rem.get_next_event_delta(), const.REMINDER_DATETIME_FORMAT)
        id_ = bc.config.ids["reminder"]
        bc.config.reminders[id_] = Reminder(
            str(new_time), rem.message, message.channel.id, bc.config.reminders[index].author,
            datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT))
        bc.config.reminders[id_].repeat_after = rem.repeat_after
        bc.config.ids["reminder"] += 1
        bc.config.reminders.pop(index)
        await Msg.response(
            message, f"Skipped reminder {index} at {rem.time}, "
                     f"next reminder {id_} will be at {bc.config.reminders[id_].time}", silent)

    @staticmethod
    async def _timeuntilreminder(message, command, silent=False):
        """Show time until particular reminder
    Example: !timeuntilreminder 1"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        rem = bc.config.reminders[index]
        rem_time = datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - datetime.datetime.now()
        if rem_time < datetime.timedelta(days=1):
            rem_time = "0 days, " + str(rem_time)
        result = f"Time until reminder {index} ('{rem.message}') is {rem_time}"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _setprereminders(message, command, silent=False):
        """Set pre reminders notifying that reminder will be sent in particular time.
        For example, send pre reminder 10 minutes before actual event (to prepare or something)
    Usage: !setprereminders <reminder_id> [<time_before_reminder_in_minutes> ...]
    Examples:
        !setprereminders 1 10
        !setprereminders 2 5 10 15"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reminder", silent)
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return null(await Msg.response(message, "Invalid index of reminder!", silent))
        rem = bc.config.reminders[index]
        prereminders_list = []
        for i in range(2, len(command)):
            time_before_reminder = await Util.parse_int(
                message, command[i], f"Parameter #{i} for '{command[0]}' should be time in minutes", silent)
            if time_before_reminder is None:
                return
            prereminders_list.append(time_before_reminder)
            if time_before_reminder <= 0:
                return null(await Msg.response(message, "Pre reminder time should be more than 0 minutes", silent))
            if time_before_reminder > 24 * 60:
                return null(await Msg.response(message, "Pre reminder time should be less than 1 day", silent))
        rem.prereminders_list = prereminders_list
        rem.used_prereminders_list = [False] * len(prereminders_list)
        result = f"Set prereminders list for reminder {index}: {', '.join([str(x) for x in rem.prereminders_list])}"
        await Msg.response(message, result, silent)

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