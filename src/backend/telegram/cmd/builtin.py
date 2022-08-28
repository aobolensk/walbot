import asyncio
import uuid

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.api.command import Command
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_message, reply
from src.config import bc
from src.log import log
from src.mail import Mail


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("authorize", self._authorize, run_async=True))
        dispatcher.add_handler(CommandHandler("resetpass", self._resetpass, run_async=True))
        dispatcher.add_handler(CommandHandler("poll", self._poll, run_async=True))

    @Mail.send_exception_info_to_admin_emails
    def _authorize(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        passphrase = context.args[0] if context.args else ""
        loop = asyncio.new_event_loop()
        if passphrase == bc.config.telegram.passphrase:
            bc.config.telegram.channel_whitelist.add(update.effective_chat.id)
            loop.run_until_complete(
                Command.send_message(TelegramExecutionContext(update), "Channel has been added to whitelist"))
        else:
            loop.run_until_complete(Command.send_message(TelegramExecutionContext(update), "Wrong passphrase!"))

    @Mail.send_exception_info_to_admin_emails
    def _resetpass(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if not check_auth(update):
            return
        loop = asyncio.new_event_loop()
        bc.config.telegram.passphrase = uuid.uuid4().hex
        log.warning("New passphrase: " + bc.config.telegram.passphrase)
        loop.run_until_complete(Command.send_message(TelegramExecutionContext(update), 'Passphrase has been reset!'))

    @Mail.send_exception_info_to_admin_emails
    def _poll(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if not check_auth(update):
            return
        if len(context.args) < 2:
            reply(update, "Usage: /poll option 1;option 2;option 3")
            return
        options = ' '.join(context.args).split(';')
        context.bot.send_poll(
            update.effective_chat.id,
            "Poll",
            options,
        )
