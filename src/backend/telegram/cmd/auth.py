import uuid

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.api.command import Command
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_command
from src.config import bc
from src.log import log
from src.mail import Mail


class AuthCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("authorize", self._authorize))
        dispatcher.add_handler(CommandHandler("resetpass", self._resetpass))

    @Mail.send_exception_info_to_admin_emails
    def _authorize(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        passphrase = context.args[0] if context.args else ""
        if passphrase == bc.config.telegram["passphrase"]:
            bc.config.telegram["channel_whitelist"].add(update.effective_chat.id)
            Command.send_message(TelegramExecutionContext(update), "Channel has been added to whitelist")
        else:
            Command.send_message(TelegramExecutionContext(update), "Wrong passphrase!")

    @Mail.send_exception_info_to_admin_emails
    def _resetpass(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.config.telegram["passphrase"] = uuid.uuid4().hex
        log.warning("New passphrase: " + bc.config.telegram["passphrase"])
        Command.send_message(TelegramExecutionContext(update), 'Passphrase has been reset!')
