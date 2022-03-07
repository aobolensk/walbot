import threading
import time

from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram.messageentity import MessageEntity

from src.config import bc
from src.bot_instance import BotInstance
from src.log import log
from src.mail import Mail
from src.backend.telegram.cmd.builtin import BuiltinCommands


class TelegramBotInstance(BotInstance):
    def __init__(self) -> None:
        self._is_stopping = False

    def start(self, args) -> None:
        threading.Thread(target=self._run, args=(args,)).start()

    @Mail.send_exception_info_to_admin_emails
    def _handle_messages(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log.info("(" + update.message.chat.title + ") " + update.message.from_user.username + ": " + text)
        bc.markov.add_string(text)

    @Mail.send_exception_info_to_admin_emails
    def _handle_mentions(self, update: Update, context: CallbackContext) -> None:
        text = update.message.text
        log.info("(" + update.message.chat.title + ") " + update.message.from_user.username + ": " + text)
        result = bc.markov.generate()
        update.message.reply_text(result)

    def _run(self, args) -> None:
        while True:
            if bc is None or bc.secret_config is None:
                time.sleep(2)
            else:
                break
        if bc.secret_config.telegram["token"] is None:
            log.warning("Telegram backend is not configured. Missing token in secret config")
            return
        log.info("Starting Telegram instance...")
        updater = Updater(bc.secret_config.telegram["token"])
        cmds = BuiltinCommands()
        cmds.add_handlers(updater.dispatcher)
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & Filters.entity(MessageEntity.MENTION), self._handle_mentions))
        updater.dispatcher.add_handler(
            MessageHandler(
                Filters.text & ~Filters.command & ~Filters.entity(MessageEntity.MENTION), self._handle_messages))

        log.info("Telegram instance is started!")
        updater.start_polling()
        while True:
            time.sleep(1)
            if self._is_stopping:
                log.info("Stopping Telegram instance...")
                updater.stop()
                log.info("Telegram instance is stopped!")
                break

    def stop(self, args) -> None:
        self._is_stopping = True
