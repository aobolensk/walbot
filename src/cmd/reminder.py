import datetime
import random
from typing import List

import dateutil.relativedelta

from src import const
from src.api.command import BaseCmd, Command, ExecutionContext, Implementation
from src.api.reminder import Reminder
from src.backend.discord.embed import DiscordEmbed
from src.backend.discord.message import Msg
from src.config import bc
from src.utils import Util


class _ReminderInternals:
    @staticmethod
    def parse_reminder_args(execution_ctx: ExecutionContext, date: str, time: str):
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
                return Command.send_message(execution_ctx, "Unexpected error during day of week processing!")
            days_delta = (weekday - datetime.datetime.today().weekday() + 7) % 7
            if days_delta == 0:
                days_delta = 7
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_delta), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = Util.parse_int_for_command(
                execution_ctx, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = Util.parse_int_for_command(
                execution_ctx, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("w"):
            weeks_amount = date[:-1]
            weeks_amount = Util.parse_int_for_command(
                execution_ctx, weeks_amount, "You need to specify amount of weeks before 'w'. Example: 2w for 2 weeks")
            if weeks_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=weeks_amount * 7), const.REMINDER_DATE_FORMAT)
        elif date.endswith("m"):
            months_amount = date[:-1]
            months_amount = Util.parse_int_for_command(
                execution_ctx, months_amount,
                "You need to specify amount of months before 'm'. Example: 3m for 3 months")
            if months_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() +
                dateutil.relativedelta.relativedelta(months=months_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("y"):
            years_amount = date[:-1]
            years_amount = Util.parse_int_for_command(
                execution_ctx, years_amount,
                "You need to specify amount of years before 'y'. Example: 3y for 3 years")
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
            return Command.send_message(
                execution_ctx,
                f"{time} does not match format {const.REMINDER_DATETIME_FORMAT}\n"
                "More information about format: <https://strftime.org/>")
        return time

    @staticmethod
    def parse_reminder_args_in(execution_ctx: ExecutionContext, time: str):
        r = const.REMINDER_IN_REGEX.match(time)
        if r is None:
            return Command.send_message(
                execution_ctx,
                ("Provide relative time in the following format: "
                 "<weeks>w<days>d<hours>h<minutes>m. "
                 "All parts except one are optional"))
        weeks = int(r.group(2)) if r.group(2) is not None else 0
        days = int(r.group(4)) if r.group(4) is not None else 0
        hours = int(r.group(6)) if r.group(6) is not None else 0
        minutes = int(r.group(8)) if r.group(8) is not None else 0
        time = (datetime.datetime.now() + datetime.timedelta(
            weeks=weeks, days=days, hours=hours, minutes=minutes)).strftime(const.REMINDER_DATETIME_FORMAT)
        return time


class ReminderCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self, commands) -> None:
        commands["reminder"] = Command(
            "reminder", "reminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._reminder)
        commands["addreminder"] = Command(
            "reminder", "addreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._addreminder)
        commands["updreminder"] = Command(
            "reminder", "updreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._updreminder)
        commands["listreminder"] = Command(
            "reminder", "listreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._listreminder)
        commands["delreminder"] = Command(
            "reminder", "delreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._delreminder)

    def _reminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return Command.send_message(execution_ctx, "Invalid index of reminder!")
        reminder = bc.config.reminders[index]
        if execution_ctx.platform == "discord":
            e = DiscordEmbed()
            e.title("Reminder info")
            e.description(reminder.message)
            e.footer(f"{reminder.author} • {datetime.datetime.strptime(reminder.time, const.REMINDER_DATETIME_FORMAT)}")
            e.add_field("Index", str(index), True)
            e.add_field("Channel", f'{reminder.backend}: <#{reminder.channel_id}>', True)
            if reminder.repeat_after:
                e.add_field("Repeats every", f"{reminder.repeat_after} {reminder.repeat_interval_measure}", True)
            e.add_field("Created", reminder.time_created, True)
            if reminder.prereminders_list:
                e.add_field("Pre reminders (in minutes)", ', '.join([str(x) for x in reminder.prereminders_list]), True)
            if reminder.notes:
                e.add_field("Notes", reminder.notes, True)
            execution_ctx.send_message(None, embed=e.get())
        else:
            result = f"Reminder {index}:\n"
            result += f"Message: {reminder.message}\n"
            result += f"Time: {datetime.datetime.strptime(reminder.time, const.REMINDER_DATETIME_FORMAT)}\n"
            result += f"Author: {reminder.author}\n"
            result += f"Channel: {reminder.backend}: <#{reminder.channel_id}>\n"
            if reminder.repeat_after:
                result += f"Repeats every: {reminder.repeat_after} {reminder.repeat_interval_measure}\n"
            result += f"Created: {reminder.time_created}\n"
            if reminder.prereminders_list:
                result += f"Pre reminders (in minutes): {', '.join([str(x) for x in reminder.prereminders_list])}\n"
            if reminder.notes:
                result += f"Notes: {reminder.notes}\n"
            Command.send_message(execution_ctx, result)

    def _addreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=4):
            return
        text = ' '.join(cmd_line[3:])
        if cmd_line[1] == "in":
            time = _ReminderInternals.parse_reminder_args_in(execution_ctx, cmd_line[2])
        else:
            time = _ReminderInternals.parse_reminder_args(execution_ctx, cmd_line[1], cmd_line[2])
        if time is None:
            return
        id_ = bc.config.ids["reminder"]
        if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
            return Command.send_message(execution_ctx, "Reminder timestamp is earlier than now")
        if execution_ctx.platform == "discord":
            bc.config.reminders[id_] = Reminder(
                str(time), text, execution_ctx.message.channel.id, execution_ctx.message.author.name,
                datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT), const.BotBackend.DISCORD)
            bc.config.ids["reminder"] += 1
            Command.send_message(execution_ctx, f"Reminder '{text}' with id {id_} added at {time}")
        else:
            Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    def _updreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=5):
            return
        index = Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return Command.send_message(execution_ctx, "Invalid index of reminder!")
        text = ' '.join(cmd_line[4:])
        if cmd_line[2] == "in":
            time = _ReminderInternals.parse_reminder_args_in(execution_ctx, cmd_line[3])
        else:
            time = _ReminderInternals.parse_reminder_args(execution_ctx, cmd_line[2], cmd_line[3])
        if time is None:
            return
        if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
            return Command.send_message(execution_ctx, "Reminder timestamp is earlier than now")
        if execution_ctx.platform == "discord":
            bc.config.reminders[index] = Reminder(
                str(time), text, execution_ctx.message.channel.id, bc.config.reminders[index].author,
                datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT), const.BotBackend.DISCORD)
            Command.send_message(
                execution_ctx, f"Successfully updated reminder {index}: '{text}' at {time}")
        else:
            Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    def _listreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if len(cmd_line) == 2:
            count = Util.parse_int_for_command(
                execution_ctx, cmd_line[1],
                f"Second parameter for '{cmd_line[0]}' should be amount of reminders to print")
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
            channel = f'{reminder.backend}: <#{reminder.channel_id}>'
            reminder_list.append(
                (reminder.time,
                 Util.cut_string(reminder.message, 256),
                 f"{notes if reminder.notes else ''}"
                 f"{index} at {reminder.time} "
                 f" in {channel}"
                 f"{rep if reminder.repeat_after else ''}"
                 f"{prereminders if reminder.prereminders_list else ''}"))
        reminder_list.sort()
        reminder_list = reminder_list[:reminders_count]
        if execution_ctx.platform == "discord":
            embed_color = random.randint(0x000000, 0xffffff)
            for reminder_chunk in Msg.split_by_chunks(reminder_list, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
                e = DiscordEmbed()
                e.title("List of reminders")
                e.color(embed_color)
                for rem in reminder_chunk:
                    e.add_field(rem[1], rem[2])
                execution_ctx.send_message(None, embed=e.get())
        else:
            result = ""
            for reminder in reminder_list:
                result += f"{reminder[0]}: {reminder[1]} {reminder[2]}\n"
            Command.send_message(execution_ctx, result)

    def _delreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if not Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        errors = []
        passed = []
        for i in range(1, len(cmd_line)):
            index = Util.parse_int_for_command(
                execution_ctx, cmd_line[i], f"Parameters for '{cmd_line[0]}' should be indexes of reminder")
            if index is None:
                return
            if index in bc.config.reminders.keys():
                passed.append(cmd_line[i])
                bc.config.reminders.pop(index)
            else:
                errors.append(cmd_line[i])
        result = ""
        if len(passed):
            if len(passed) > 1:
                result += "Successfully deleted reminders #"
            else:
                result += "Successfully deleted reminder #"
            result += ', '.join(map(str, passed)) + '\n'
        if len(errors):
            if len(errors) > 1:
                result += "Invalid reminder indexes: "
            else:
                result += "Invalid reminder index: "
            result += ', '.join(map(str, errors))
        Command.send_message(execution_ctx, result)
