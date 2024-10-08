import asyncio
import time

from telegram import Update, constants
from telegram.error import NetworkError
from telegram.ext import Application, CallbackContext, MessageHandler, filters

from src import const
from src.api.bot_instance import BotInstance
from src.backend.telegram.command import (
    CommonCommandsHandlers,
    TelegramCommandBinding
)
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
    async def _handle_messages(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.message_cache.push(update.message.chat.id, CachedMsg(text, str(update.message.from_user.id)))
        bc.markov.add_string(text)
        await MessageProcessing.process_responses(TelegramExecutionContext(update, context), text)
        await MessageProcessing.process_repetitions(TelegramExecutionContext(update, context))
        await bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update, context))

    @Mail.send_exception_info_to_admin_emails
    async def _handle_mentions(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.message_cache.push(update.message.chat.id, CachedMsg(text, str(update.message.from_user.id)))
        cmd_line = bc.config.on_mention_command.split(" ")
        await bc.executor.commands[cmd_line[0]].run(cmd_line, TelegramExecutionContext(update, context))
        await bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update, context))

    @staticmethod
    async def _error_handler(update: Update, context: CallbackContext) -> None:
        # You can also log the error or do other error handling here
        error = context.error
        if isinstance(error, NetworkError):
            log.error(f"Network error occurred: {error}")
            return
        raise error

    @Mail.send_exception_info_to_admin_emails
    def _run(self, args) -> None:
        log.info("Starting Telegram instance...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = Application.builder().token(bc.secret_config.telegram["token"]).build()
        if Util.proxy.http() is not None:
            log.info("Telegram instance is using proxy: " + Util.proxy.http())
        common_cmds = CommonCommandsHandlers()
        common_cmds.add_handlers(app)
        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & filters.Entity(
                    constants.MessageEntityType.MENTION), self._handle_mentions))
        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.Entity(
                    constants.MessageEntityType.MENTION), self._handle_messages))

        log.info("Telegram instance is started!")
        bc.telegram.bot_username = loop.run_until_complete(app.bot.get_me()).username
        bc.be.set_running(const.BotBackend.TELEGRAM, True, f"{bc.telegram.bot_username} ({self.__class__.__name__})")
        bc.executor.binders[const.BotBackend.TELEGRAM] = TelegramCommandBinding(app)
        bc.telegram.app = app
        app.add_error_handler(self._error_handler)
        app.run_polling(timeout=600, stop_signals=())
        counter = 0
        reminder_proc = ReminderProcessing()
        while True:
            time.sleep(1)
            counter += 1
            if self._is_stopping:
                log.info("Stopping Telegram instance...")
                loop.run_until_complete(app.stop())
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
