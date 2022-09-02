import asyncio
import datetime
import time
from urllib.parse import quote_plus

from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater
from telegram.messageentity import MessageEntity

from src import const
from src.api.bot_instance import BotInstance
from src.api.reminder import Reminder
from src.backend.telegram.cmd.builtin import BuiltinCommands
from src.backend.telegram.cmd.common import CommonCommands
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import (check_auth, escape_markdown_text,
                                       log_message)
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log
from src.mail import Mail
from src.utils import Util


class TelegramBotInstance(BotInstance):
    def __init__(self) -> None:
        self._is_stopping = False

    def start(self, args, *rest, **kwargs) -> None:
        self._run(args)

    @Mail.send_exception_info_to_admin_emails
    def _handle_messages(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.markov.add_string(text)

    @Mail.send_exception_info_to_admin_emails
    def _handle_mentions(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if not check_auth(update):
            return
        cmd_line = bc.config.on_mention_command.split(" ")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(bc.executor.commands[cmd_line[0]].run(cmd_line, TelegramExecutionContext(update)))

    @Mail.send_exception_info_to_admin_emails
    def _send_message(self, chat_id: int, text: str) -> None:
        log.info(f"({chat_id}) /sendMessage: " + text)
        text = quote_plus(escape_markdown_text(text))
        url = (
            f"https://api.telegram.org/bot{bc.secret_config.telegram['token']}/sendMessage"
            f"?chat_id={chat_id}&text={text}&parse_mode=MarkdownV2"
        )
        rq = Util.request(url)
        r = rq.get()
        if r.status_code != 200:
            log.error(f"Error sending message to {chat_id}: {r.status_code} {r.json()}")

    @Mail.send_exception_info_to_admin_emails
    def _process_reminders_iteration(self) -> None:
        log.debug3("Telegram: Reminder processing iteration has started")
        now = datetime.datetime.now().replace(second=0).strftime(const.REMINDER_DATETIME_FORMAT)
        to_remove = []
        to_append = []
        reminder_do_not_update_flag = False
        for key, rem in bc.config.reminders.items():
            if rem.backend != "telegram":
                continue
            for i in range(len(rem.prereminders_list)):
                prereminder = rem.prereminders_list[i]
                used_prereminder = rem.used_prereminders_list[i]
                if prereminder == 0 or used_prereminder:
                    continue
                prereminder_time = (
                    datetime.datetime.now().replace(second=0) + datetime.timedelta(minutes=prereminder))
                if rem == prereminder_time.strftime(const.REMINDER_DATETIME_FORMAT):
                    result = f"{prereminder} minutes left until reminder\n"
                    result += rem.message + "\n" + rem.notes + "\n"
                    self._send_message(rem.channel_id, result)
                    rem.used_prereminders_list[i] = True
            if rem == now:
                result = (' '.join(rem.ping_users) + "\n") if rem.ping_users else ""
                result += f"⏰ You asked to remind at {now}\n"
                result += rem.message + "\n" + rem.notes + "\n"
                self._send_message(rem.channel_id, result)
                for user_id in rem.telegram_whisper_users:
                    self._send_message(user_id, result)
                if rem.email_users:
                    mail = Mail(bc.secret_config)
                    mail.send(
                        rem.email_users,
                        f"Reminder: {rem.message}",
                        f"You asked to remind at {now} -> {rem.message}")
                if rem.repeat_after > 0:
                    new_time = datetime.datetime.now().replace(second=0, microsecond=0) + rem.get_next_event_delta()
                    new_time = new_time.strftime(const.REMINDER_DATETIME_FORMAT)
                    to_append.append(
                        Reminder(
                            str(new_time), rem.message, rem.channel_id, rem.author,
                            rem.time_created, const.BotBackend.TELEGRAM))
                    to_append[-1].repeat_after = rem.repeat_after
                    to_append[-1].repeat_interval_measure = rem.repeat_interval_measure
                    to_append[-1].prereminders_list = rem.prereminders_list
                    to_append[-1].used_prereminders_list = [False] * len(rem.prereminders_list)
                    to_append[-1].discord_whisper_users = rem.discord_whisper_users
                    to_append[-1].telegram_whisper_users = rem.telegram_whisper_users
                    to_append[-1].notes = rem.notes
                    log.debug2(f"Scheduled renew of recurring reminder - old id: {key}")
                to_remove.append(key)
            elif rem < now:
                log.debug2(f"Scheduled reminder with id {key} removal")
                to_remove.append(key)
            else:
                prereminders_delay = 0
                if rem.prereminders_list:
                    prereminders_delay = max(rem.prereminders_list)
                if ((datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - datetime.datetime.now())
                        < datetime.timedelta(minutes=(5 + prereminders_delay / 60))):
                    reminder_do_not_update_flag = True
        bc.do_not_update[DoNotUpdateFlag.TELEGRAM_REMINDER] = reminder_do_not_update_flag
        for key in to_remove:
            bc.config.reminders.pop(key)
        for item in to_append:
            key = bc.config.ids["reminder"]
            bc.config.reminders[key] = item
            bc.config.ids["reminder"] += 1
        log.debug3("Telegram: Reminder processing iteration has finished")

    def _run(self, args) -> None:
        if bc.secret_config.telegram["token"] is None:
            log.warning("Telegram backend is not configured. Missing token in secret config")
            return
        log.info("Starting Telegram instance...")
        updater = Updater(bc.secret_config.telegram["token"], request_kwargs={
            "proxy_url": Util.proxy.http(),
        })
        if Util.proxy.http() is not None:
            log.info("Telegram instance is using proxy: " + Util.proxy.http())
        builtin_cmds = BuiltinCommands()
        builtin_cmds.add_handlers(updater.dispatcher)
        common_cmds = CommonCommands()
        common_cmds.add_handlers(updater.dispatcher)
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & Filters.entity(MessageEntity.MENTION), self._handle_mentions))
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & ~Filters.entity(MessageEntity.MENTION), self._handle_messages))

        log.info("Telegram instance is started!")
        bc.backends["telegram"] = True
        bc.telegram.bot_username = updater.bot.name
        bc.telegram.dispatcher = updater.dispatcher
        updater.start_polling(timeout=600)
        counter = 0
        while True:
            time.sleep(1)
            counter += 1
            if self._is_stopping:
                log.info("Stopping Telegram instance...")
                updater.stop()
                log.info("Telegram instance is stopped!")
                break
            if counter % const.REMINDER_POLLING_INTERVAL == 0:
                try:
                    self._process_reminders_iteration()
                except Exception as e:
                    log.error(f"Error in processing reminders: {e}")

    def stop(self, args, main_bot=True) -> None:
        self._is_stopping = True
