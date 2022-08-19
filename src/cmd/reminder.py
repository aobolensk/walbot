import datetime
from typing import List

import dateutil.relativedelta

from src import const
from src.api.command import BaseCmd, Command, ExecutionContext, Implementation
from src.api.reminder import Reminder
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
        commands["addreminder"] = Command(
            "reminder", "addreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._addreminder)

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
