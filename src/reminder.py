import datetime
import random

from src import const
from src.api.execution_context import ExecutionContext
from src.api.reminder import Reminder
from src.backend.discord.embed import DiscordEmbed
from src.backend.discord.message import Msg
from src.backend.telegram.util import send_message
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.emoji import get_clock_emoji
from src.log import log
from src.mail import Mail
from src.utils import Time


class ReminderProcessing:
    @Mail.send_exception_info_to_admin_emails
    async def iteration(execution_ctx: ExecutionContext, backend: const.BotBackend) -> None:
        """This function is called no less than 1 time per minute"""
        log.debug3(f"{backend}: Reminder processing iteration has started")
        now = Time().now().replace(second=0).strftime(const.REMINDER_DATETIME_FORMAT)
        to_remove = []
        to_append = []
        reminder_do_not_update_flag = False
        for key, rem in bc.config.reminders.items():
            if rem.backend != str(backend):
                continue
            for i in range(len(rem.prereminders_list)):
                prereminder = rem.prereminders_list[i]
                used_prereminder = rem.used_prereminders_list[i]
                if prereminder == 0 or used_prereminder:
                    continue
                prereminder_time = (
                    Time().now().replace(second=0) + datetime.timedelta(minutes=prereminder))
                if rem == prereminder_time.strftime(const.REMINDER_DATETIME_FORMAT):
                    if backend == const.BotBackend.DISCORD:
                        channel = bc.discord.get_channel(rem.channel_id)
                        e = DiscordEmbed()
                        clock_emoji = get_clock_emoji(Time().now().strftime("%H:%M"))
                        e.title(f"{prereminder} minutes left until reminder")
                        e.description(rem.message + "\n" + rem.notes)
                        e.color(random.randint(0x000000, 0xffffff))
                        e.timestamp(
                            datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=prereminder))
                        e.footer(text=rem.author)
                        await channel.send("", embed=e.get())
                    elif backend == const.BotBackend.TELEGRAM:
                        result = f"{prereminder} minutes left until reminder\n"
                        result += rem.message + "\n" + rem.notes + "\n"
                        send_message(rem.channel_id, result)
                    else:
                        log.error(f"ReminderProcessing: backend '{backend}' is not supported")
                    rem.used_prereminders_list[i] = True
            if rem == now:
                if backend == const.BotBackend.DISCORD:
                    channel = bc.discord.get_channel(rem.channel_id)
                    clock_emoji = get_clock_emoji(Time().now().strftime("%H:%M"))
                    e = DiscordEmbed()
                    e.title(f"{clock_emoji} You asked to remind")
                    e.description(rem.message + "\n" + rem.notes)
                    e.color(random.randint(0x000000, 0xffffff))
                    e.timestamp(datetime.datetime.now(datetime.timezone.utc))
                    e.footer(text=rem.author)
                    await channel.send(' '.join(rem.ping_users if rem.ping_users else ""), embed=e.get())
                    for user_id in rem.discord_whisper_users:
                        await Msg.send_direct_message(
                            bc.discord.get_user(user_id), f"You asked to remind at {now} -> {rem.message}", False)
                elif backend == const.BotBackend.TELEGRAM:
                    result = (' '.join(rem.ping_users) + "\n") if rem.ping_users else ""
                    clock_emoji = get_clock_emoji(Time().now().strftime("%H:%M"))
                    result += f"{clock_emoji} You asked to remind at {now}\n"
                    result += rem.message + "\n" + rem.notes + "\n"
                    send_message(rem.channel_id, result)
                    for user_id in rem.telegram_whisper_users:
                        send_message(user_id, result)
                else:
                    log.error(f"ReminderProcessing: backend '{backend}' is not supported")
                if rem.email_users:
                    mail = Mail(bc.secret_config)
                    mail.send(
                        rem.email_users,
                        f"Reminder: {rem.message}",
                        f"You asked to remind at {now} -> {rem.message}")
                if rem.repeat_after > 0:
                    new_time = Time().now().replace(second=0, microsecond=0) + rem.get_next_event_delta()
                    if (rem.remaining_repetitions != 0 and
                            (rem.limit_repetitions_time is None or new_time <= datetime.datetime.strptime(
                                rem.limit_repetitions_time, const.REMINDER_DATETIME_FORMAT))):
                        new_time = new_time.strftime(const.REMINDER_DATETIME_FORMAT)
                        to_append.append(
                            Reminder(
                                str(new_time), rem.message, rem.channel_id, rem.author, rem.time_created, backend))
                        to_append[-1].repeat_after = rem.repeat_after
                        to_append[-1].repeat_interval_measure = rem.repeat_interval_measure
                        to_append[-1].prereminders_list = rem.prereminders_list
                        to_append[-1].used_prereminders_list = [False] * len(rem.prereminders_list)
                        to_append[-1].discord_whisper_users = rem.discord_whisper_users
                        to_append[-1].telegram_whisper_users = rem.telegram_whisper_users
                        to_append[-1].notes = rem.notes
                        to_append[-1].remaining_repetitions = (
                            rem.remaining_repetitions - 1 if rem.remaining_repetitions != -1 else -1)
                        to_append[-1].limit_repetitions_time = rem.limit_repetitions_time
                    log.debug2(f"Scheduled renew of recurring reminder - old id: {key}")
                to_remove.append(key)
            elif rem < now:
                log.debug2(f"Scheduled reminder with id {key} removal")
                to_remove.append(key)
            else:
                prereminders_delay = 0
                if rem.prereminders_list:
                    prereminders_delay = max(rem.prereminders_list)
                if ((datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - Time().now())
                        < datetime.timedelta(minutes=(5 + prereminders_delay / 60))):
                    reminder_do_not_update_flag = True
        if backend == const.BotBackend.DISCORD:
            bc.do_not_update[DoNotUpdateFlag.DISCORD_REMINDER] = reminder_do_not_update_flag
        elif backend == const.BotBackend.TELEGRAM:
            bc.do_not_update[DoNotUpdateFlag.TELEGRAM_REMINDER] = reminder_do_not_update_flag
        else:
            log.error(f"ReminderProcessing: backend '{backend}' is not supported")
        for key in to_remove:
            bc.config.reminders.pop(key)
        for item in to_append:
            key = bc.config.ids["reminder"]
            bc.config.reminders[key] = item
            bc.config.ids["reminder"] += 1
        log.debug3(f"{backend}: Reminder processing iteration has finished")
