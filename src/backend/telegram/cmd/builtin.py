import uuid

from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler

from src import const
from src.api.command import Command
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_message
from src.config import User, bc
from src.log import log
from src.mail import Mail


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, app: Application) -> None:
        app.add_handler(CommandHandler("authorize", self._authorize))
        app.add_handler(CommandHandler("resetpass", self._resetpass))
        app.add_handler(CommandHandler("help", self._help))

    @Mail.send_exception_info_to_admin_emails
    async def _authorize(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if update.message.from_user.id not in bc.config.telegram.users.keys():
            bc.config.telegram.users[update.message.from_user.id] = User(update.message.from_user.id)
        passphrase = context.args[0] if context.args else ""
        if passphrase == bc.config.telegram.passphrase:
            bc.config.telegram.channel_whitelist.add(update.effective_chat.id)
            await Command.send_message(TelegramExecutionContext(update), "Channel has been added to whitelist")
        else:
            await Command.send_message(TelegramExecutionContext(update), "Wrong passphrase!")

    @Mail.send_exception_info_to_admin_emails
    async def _resetpass(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if not check_auth(update):
            return
        bc.config.telegram.passphrase = uuid.uuid4().hex
        log.warning("New passphrase: " + bc.config.telegram.passphrase)
        await Command.send_message(TelegramExecutionContext(update), 'Passphrase has been reset!')

    @Mail.send_exception_info_to_admin_emails
    async def _help(self, update: Update, context: CallbackContext) -> None:
        log_message(update)
        if not check_auth(update):
            return
        version = bc.info.version
        result = f"Built-in commands help: {const.GIT_REPO_LINK}/blob/{version}/{const.TELEGRAM_COMMANDS_DOC_PATH}"
        await Command.send_message(TelegramExecutionContext(update), result)
