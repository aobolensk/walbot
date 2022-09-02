import datetime
import random
from typing import List, Optional

import dateutil.relativedelta

from src import const
from src.api.command import (BaseCmd, Command, Implementation,
                             SupportedPlatforms)
from src.api.execution_context import ExecutionContext
from src.api.reminder import Reminder
from src.backend.discord.embed import DiscordEmbed
from src.backend.discord.message import Msg
from src.config import bc
from src.utils import Util


class _ReminderInternals:
    @staticmethod
    async def parse_reminder_args(execution_ctx: ExecutionContext, date: str, time: str):
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
                return await Command.send_message(execution_ctx, "Unexpected error during day of week processing!")
            days_delta = (weekday - datetime.datetime.today().weekday() + 7) % 7
            if days_delta == 0:
                days_delta = 7
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_delta), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = await Util.parse_int_for_command(
                execution_ctx, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("d"):
            days_amount = date[:-1]
            days_amount = await Util.parse_int_for_command(
                execution_ctx, days_amount, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if days_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=days_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("w"):
            weeks_amount = date[:-1]
            weeks_amount = await Util.parse_int_for_command(
                execution_ctx, weeks_amount, "You need to specify amount of weeks before 'w'. Example: 2w for 2 weeks")
            if weeks_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() + datetime.timedelta(days=weeks_amount * 7), const.REMINDER_DATE_FORMAT)
        elif date.endswith("m"):
            months_amount = date[:-1]
            months_amount = await Util.parse_int_for_command(
                execution_ctx, months_amount,
                "You need to specify amount of months before 'm'. Example: 3m for 3 months")
            if months_amount is None:
                return
            date = datetime.datetime.strftime(
                datetime.datetime.now() +
                dateutil.relativedelta.relativedelta(months=months_amount), const.REMINDER_DATE_FORMAT)
        elif date.endswith("y"):
            years_amount = date[:-1]
            years_amount = await Util.parse_int_for_command(
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
            return await Command.send_message(
                execution_ctx,
                f"{time} does not match format {const.REMINDER_DATETIME_FORMAT}\n"
                "More information about format: <https://strftime.org/>")
        return time

    @staticmethod
    async def parse_reminder_args_in(execution_ctx: ExecutionContext, time: str):
        r = const.REMINDER_IN_REGEX.match(time)
        if r is None:
            return await Command.send_message(
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

    @staticmethod
    async def listreminder_common(cmd_line: List[str], execution_ctx: ExecutionContext, is_only_locals=False) -> None:
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if len(cmd_line) == 2:
            count = await Util.parse_int_for_command(
                execution_ctx, cmd_line[1],
                f"Second parameter for '{cmd_line[0]}' should be amount of reminders to print")
            if count is None:
                return
            reminders_count = count
        else:
            reminders_count = len(bc.config.reminders)
        reminder_list = []
        for index, reminder in bc.config.reminders.items():
            if is_only_locals and reminder.channel_id != execution_ctx.channel_id():
                continue
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
                await execution_ctx.send_message(None, embed=e.get())
            if not reminder_list:
                e = DiscordEmbed()
                e.title("List of reminders")
                e.color(embed_color)
                e.add_field("No reminders found!", "Use `!addreminder` command to add new reminders")
                await execution_ctx.send_message(None, embed=e.get())
        else:
            result = ""
            for reminder in reminder_list:
                result += f"{reminder[0]}: {reminder[1]} {reminder[2]}\n"
            if result:
                await Command.send_message(execution_ctx, result)
            else:
                await Command.send_message(execution_ctx, "No reminders found!")


class ReminderCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["reminder"] = Command(
            "reminder", "reminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._reminder)
        bc.executor.commands["addreminder"] = Command(
            "reminder", "addreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addreminder,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["updreminder"] = Command(
            "reminder", "updreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._updreminder,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["listreminder"] = Command(
            "reminder", "listreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listreminder)
        bc.executor.commands["listreminderlocal"] = Command(
            "reminder", "listreminderlocal", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listreminderlocal)
        bc.executor.commands["delreminder"] = Command(
            "reminder", "delreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delreminder)
        bc.executor.commands["remindme"] = Command(
            "reminder", "remindme", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._remindme,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["remindwme"] = Command(
            "reminder", "remindwme", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._remindwme,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["remindeme"] = Command(
            "reminder", "remindeme", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._remindeme)
        bc.executor.commands["repeatreminder"] = Command(
            "reminder", "repeatreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._repeatreminder)
        bc.executor.commands["skipreminder"] = Command(
            "reminder", "skipreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._skipreminder)
        bc.executor.commands["timeuntilreminder"] = Command(
            "reminder", "timeuntilreminder", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._timeuntilreminder)
        bc.executor.commands["setprereminders"] = Command(
            "reminder", "setprereminders", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setprereminders)
        bc.executor.commands["addremindernotes"] = Command(
            "reminder", "addremindernotes", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addremindernotes)
        bc.executor.commands["setreminderchannel"] = Command(
            "reminder", "setreminderchannel", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._setreminderchannel)

    async def _reminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print information about reminder
    Example:
        !reminder 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
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
            await execution_ctx.send_message(None, embed=e.get())
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
            await Command.send_message(execution_ctx, result)

    async def _addreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
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
        if not await Command.check_args_count(execution_ctx, cmd_line, min=4):
            return
        text = ' '.join(cmd_line[3:])
        if cmd_line[1] == "in":
            time = await _ReminderInternals.parse_reminder_args_in(execution_ctx, cmd_line[2])
        else:
            time = await _ReminderInternals.parse_reminder_args(execution_ctx, cmd_line[1], cmd_line[2])
        if time is None:
            return
        id_ = bc.config.ids["reminder"]
        if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
            return await Command.send_message(execution_ctx, "Reminder timestamp is earlier than now")
        if execution_ctx.platform == "discord":
            bc.config.reminders[id_] = Reminder(
                str(time), text, execution_ctx.message.channel.id, execution_ctx.message.author.name,
                datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT), const.BotBackend.DISCORD)
            bc.config.ids["reminder"] += 1
            await Command.send_message(execution_ctx, f"Reminder '{text}' with id {id_} added at {time}")
        elif execution_ctx.platform == "telegram":
            username = (
                execution_ctx.update.message.from_user.username or execution_ctx.update.message.from_user.full_name)
            bc.config.reminders[id_] = Reminder(
                str(time), text, execution_ctx.update.message.chat.id, username,
                datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT), const.BotBackend.TELEGRAM)
            bc.config.ids["reminder"] += 1
            await Command.send_message(execution_ctx, f"Reminder '{text}' with id {id_} added at {time}")
        else:
            await Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    async def _updreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
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
        if not await Command.check_args_count(execution_ctx, cmd_line, min=5):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        text = ' '.join(cmd_line[4:])
        if cmd_line[2] == "in":
            time = await _ReminderInternals.parse_reminder_args_in(execution_ctx, cmd_line[3])
        else:
            time = await _ReminderInternals.parse_reminder_args(execution_ctx, cmd_line[2], cmd_line[3])
        if time is None:
            return
        if datetime.datetime.strptime(str(time), const.REMINDER_DATETIME_FORMAT) < datetime.datetime.now():
            return await Command.send_message(execution_ctx, "Reminder timestamp is earlier than now")
        if execution_ctx.platform in ("discord", "telegram"):
            bc.config.reminders[index].time = str(time)
            bc.config.reminders[index].message = text
            bc.config.reminders[index].channel_id = execution_ctx.channel_id()
            bc.config.reminders[index].time_created = datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT)
            await Command.send_message(execution_ctx, f"Successfully updated reminder {index}: '{text}' at {time}")
        else:
            await Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    async def _listreminderlocal(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of reminders for current channel
    Examples:
        !listreminderlocal
        !listreminderlocal 5 <- prints only first 5 reminders"""

        await _ReminderInternals.listreminder_common(cmd_line, execution_ctx, is_only_locals=True)

    async def _listreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of reminders
    Examples:
        !listreminder
        !listreminder 5 <- prints only first 5 reminders"""

        await _ReminderInternals.listreminder_common(cmd_line, execution_ctx)

    async def _delreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete reminders by index
    Example: !delreminder 0 1 2"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        errors = []
        passed = []
        for i in range(1, len(cmd_line)):
            index = await Util.parse_int_for_command(
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
        await Command.send_message(execution_ctx, result)

    async def _remindme(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Ask bot to ping you when it sends reminder
    Example: !remindme 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, f"Reminder with index {index} not found")
        bc.config.reminders[index].ping_users.append(execution_ctx.message_author())
        await Command.send_message(execution_ctx, f"You will be mentioned when reminder {index} is sent")

    async def _remindwme(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Ask bot to send direct message you when it sends reminder
    Example: !remindwme 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.check_args_count(execution_ctx, "Invalid index of reminder!")
        if execution_ctx.platform == "discord":
            bc.config.reminders[index].discord_whisper_users.append(execution_ctx.message_author_id())
            await Command.send_message(
                execution_ctx, f"You will be notified in direct messages when reminder {index} is sent")
        elif execution_ctx.platform == "telegram":
            bc.config.reminders[index].telegram_whisper_users.append(execution_ctx.message_author_id())
            await Command.send_message(
                execution_ctx, f"You will be notified in direct messages when reminder {index} is sent")
        else:
            await Command.send_message(
                execution_ctx,
                f"'{cmd_line[0]}' command is not implemented on '{execution_ctx.platform}' platform")

    async def _remindeme(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Ask bot to send you an e-mail when it sends reminder
    Example: !remindeme 1 <your-email-address>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        email = cmd_line[2]
        if index not in bc.config.reminders.keys():
            await Command.send_message(execution_ctx, "Invalid index of reminder!")
        bc.config.reminders[index].email_users.append(email)
        await Command.send_message(execution_ctx, f"E-mail will be sent to '{email}' when reminder {index} is sent")

    async def _repeatreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
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
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")

        if cmd_line[2] == "hourly":
            cmd_line[2] = "1h"
        elif cmd_line[2] == "daily":
            cmd_line[2] = "1d"
        elif cmd_line[2] == "weekly":
            cmd_line[2] = "1w"
        elif cmd_line[2] == "monthly":
            cmd_line[2] = "1m"
        elif cmd_line[2] == "annually":
            cmd_line[2] = "1y"

        if cmd_line[2].endswith("h"):
            duration = cmd_line[2][:-1]
            duration = await Util.parse_int_for_command(
                execution_ctx, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if duration is None:
                return
            duration *= 60
        elif cmd_line[2].endswith("d"):
            duration = cmd_line[2][:-1]
            duration = await Util.parse_int_for_command(
                execution_ctx, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if duration is None:
                return
            duration *= 1440
        elif cmd_line[2].endswith("w"):
            duration = cmd_line[2][:-1]
            duration = await Util.parse_int_for_command(
                execution_ctx, duration, "You need to specify amount of days before 'd'. Example: 3d for 3 days")
            if duration is None:
                return
            duration *= 10080
        elif cmd_line[2].endswith("m"):
            duration = cmd_line[2][:-1]
            duration = await Util.parse_int_for_command(
                execution_ctx, duration, "You need to specify amount of days before 'm'. Example: 3m for 3 months")
            if duration is None:
                return
            bc.config.reminders[index].repeat_interval_measure = "months"
        elif cmd_line[2].endswith("y"):
            duration = cmd_line[2][:-1]
            duration = await Util.parse_int_for_command(
                execution_ctx, duration, "You need to specify amount of days before 'y'. Example: 3y for 3 years")
            if duration is None:
                return
            bc.config.reminders[index].repeat_interval_measure = "years"
        else:
            duration = await Util.parse_int_for_command(
                execution_ctx, cmd_line[2],
                f"Third parameter for '{cmd_line[0]}' should be duration of period between reminders")
            if duration is None:
                return
        if duration < 0:
            return await Command.send_message(
                execution_ctx, "Duration should be positive or zero (to disable repetition)!")
        bc.config.reminders[index].repeat_after = duration
        if duration == 0:
            return await Command.send_message(execution_ctx, f"Repetition is disabled for reminder {index}")
        await Command.send_message(
            execution_ctx,
            f"Reminder {index} will be repeated every {duration} "
            f"{bc.config.reminders[index].repeat_interval_measure}!")

    async def _skipreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Skip next instance of recurring (repeating) reminder
    Example: !skipreminder 1
    Note: only recurring (repeating) reminders are affected by this command"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        if bc.config.reminders[index].repeat_after == 0:
            return await Command.send_message(execution_ctx, "This reminder is not recurring!")
        rem = bc.config.reminders[index]
        new_time = datetime.datetime.strftime(
            datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) +
            rem.get_next_event_delta(), const.REMINDER_DATETIME_FORMAT)
        id_ = bc.config.ids["reminder"]
        bc.config.reminders[id_] = Reminder(
            str(new_time), rem.message, rem.channel_id, rem.author,
            datetime.datetime.now().strftime(const.REMINDER_DATETIME_FORMAT), rem.backend)
        bc.config.reminders[id_].repeat_after = rem.repeat_after
        bc.config.reminders[id_].repeat_interval_measure = rem.repeat_interval_measure
        bc.config.reminders[id_].prereminders_list = rem.prereminders_list
        bc.config.reminders[id_].used_prereminders_list = rem.used_prereminders_list
        bc.config.reminders[id_].discord_whisper_users = rem.discord_whisper_users
        bc.config.reminders[id_].telegram_whisper_users = rem.telegram_whisper_users
        bc.config.ids["reminder"] += 1
        bc.config.reminders.pop(index)
        await Command.send_message(
            execution_ctx,
            f"Skipped reminder {index} at {rem.time}, next reminder {id_} "
            f"will be at {bc.config.reminders[id_].time}")

    async def _timeuntilreminder(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Show time until particular reminder
    Example: !timeuntilreminder 1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        rem = bc.config.reminders[index]
        rem_time = datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - datetime.datetime.now()
        if rem_time < datetime.timedelta(days=1):
            rem_time = "0 days, " + str(rem_time)
        result = f"Time until reminder {index} ('{rem.message}') is {rem_time}"
        await Command.send_message(execution_ctx, result)
        return result

    async def _setprereminders(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set pre reminders notifying that reminder will be sent in particular time.
        For example, send pre reminder 10 minutes before actual event (to prepare or something)
    Usage: !setprereminders <reminder_id> [<time_before_reminder_in_minutes> ...]
    Examples:
        !setprereminders 1 10
        !setprereminders 2 5 10 15"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        rem = bc.config.reminders[index]
        prereminders_list = []
        for i in range(2, len(cmd_line)):
            time_before_reminder = await Util.parse_int_for_command(
                execution_ctx, cmd_line[i], f"Parameter #{i} for '{cmd_line[0]}' should be time in minutes")
            if time_before_reminder is None:
                return
            prereminders_list.append(time_before_reminder)
            if time_before_reminder <= 0:
                return await Command.send_message(execution_ctx, "Pre reminder time should be more than 0 minutes")
            if time_before_reminder > 24 * 60:
                return await Command.send_message(execution_ctx, "Pre reminder time should be less than 1 day")
        rem.prereminders_list = prereminders_list
        rem.used_prereminders_list = [False] * len(prereminders_list)
        result = f"Set prereminders list for reminder {index}: {', '.join([str(x) for x in rem.prereminders_list])}"
        await Command.send_message(execution_ctx, result)

    async def _addremindernotes(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add reminder notes
    Example: !addremindernotes 1 Some text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        rem = bc.config.reminders[index]
        rem.notes = ' '.join(cmd_line[2:])
        await Command.send_message(execution_ctx, f"Set notes for reminder {index}: {rem.notes}")

    async def _setreminderchannel(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set channel where reminder will be sent
    Example: !setreminderchannel 1 <channel_id>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3, max=3):
            return
        index = await Util.parse_int_for_command(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reminder")
        if index is None:
            return
        if index not in bc.config.reminders.keys():
            return await Command.send_message(execution_ctx, "Invalid index of reminder!")
        rem = bc.config.reminders[index]
        channel_id = await Util.parse_int_for_command(
            execution_ctx, cmd_line[2], f"Third parameter for '{cmd_line[0]}' should be channel id")
        if channel_id is None:
            return
        rem.channel_id = channel_id
        await Command.send_message(execution_ctx, f"Set channel id {channel_id} for reminder {index}")
