import asyncio
import time

from telegram import Update, constants
from telegram.ext import Application, CallbackContext, MessageHandler, filters

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
    async def _handle_messages(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.message_cache.push(update.message.chat.id, CachedMsg(text, str(update.message.from_user.id)))
        bc.markov.add_string(text)
        await MessageProcessing.process_responses(TelegramExecutionContext(update), text)
        await MessageProcessing.process_repetitions(TelegramExecutionContext(update))
        await bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    async def _handle_mentions(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log_message(update)
        if not check_auth(update):
            return
        bc.message_cache.push(update.message.chat.id, CachedMsg(text, str(update.message.from_user.id)))
        cmd_line = bc.config.on_mention_command.split(" ")
        await bc.executor.commands[cmd_line[0]].run(cmd_line, TelegramExecutionContext(update))
        await bc.plugin_manager.broadcast_command("on_message", TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _run(self, args) -> None:
        log.info("Starting Telegram instance...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = Application.builder().token(bc.secret_config.telegram["token"]).build()
        if Util.proxy.http() is not None:
            log.info("Telegram instance is using proxy: " + Util.proxy.http())
        builtin_cmds = BuiltinCommands()
        builtin_cmds.add_handlers(app)
        common_cmds = CommonCommands()
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
        bc.be.set_running(const.BotBackend.TELEGRAM, True)
        bc.executor.binders[const.BotBackend.TELEGRAM] = TelegramCommandBinding(app)
        bc.telegram.bot_username = "TODO"
        bc.telegram.app = app
        app.run_polling(timeout=600, stop_signals=())
        counter = 0
        reminder_proc = ReminderProcessing()
        while True:
            time.sleep(1)
            counter += 1
            if self._is_stopping:
                log.info("Stopping Telegram instance...")
                app.stop()
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
