import asyncio
import time

from telegram import Update
from telegram.ext import CallbackContext, Filters, MessageHandler, Updater
from telegram.messageentity import MessageEntity

from src import const
from src.api.bot_instance import BotInstance
from src.backend.telegram.cmd.builtin import BuiltinCommands
from src.backend.telegram.cmd.common import CommonCommands
from src.backend.telegram.command import TelegramCommandBinding
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_message
from src.config import bc
from src.log import log
from src.mail import Mail
from src.message_cache import CachedMsg
from src.message_processing import MessageProcessing
from src.reminder import ReminderProcessing
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
        bc.message_cache.push(str(update.message.chat.id), CachedMsg(text, str(update.message.from_user.id)))
        bc.markov.add_string(text)
        loop = asyncio.new_event_loop()
        loop.run_until_complete(MessageProcessing.process_responses(TelegramExecutionContext(update), text))
        loop.run_until_complete(bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update)))

    @Mail.send_exception_info_to_admin_emails
    def _handle_mentions(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.message_cache.push(str(update.message.chat.id), CachedMsg(text, str(update.message.from_user.id)))
        cmd_line = bc.config.on_mention_command.split(" ")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(bc.executor.commands[cmd_line[0]].run(cmd_line, TelegramExecutionContext(update)))
        loop.run_until_complete(bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update)))

    @Mail.send_exception_info_to_admin_emails
    def _run(self, args) -> None:
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
        bc.executor.binders[const.BotBackend.TELEGRAM] = TelegramCommandBinding(updater.dispatcher)
        bc.telegram.bot_username = updater.bot.name
        bc.telegram.dispatcher = updater.dispatcher
        updater.start_polling(timeout=600)
        counter = 0
        loop = asyncio.new_event_loop()
        reminder_proc = ReminderProcessing()
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
                    loop.run_until_complete(reminder_proc.iteration(const.BotBackend.TELEGRAM))
                except Exception as e:
                    log.error(f"Error in processing reminders: {e}")

    def stop(self, args, main_bot=True) -> None:
        self._is_stopping = True

    def has_credentials(self):
        return bc.secret_config.telegram["token"] is not None
