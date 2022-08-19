from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_command
from src.config import bc
from src.mail import Mail


class ReminderCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("listreminder", self._listreminder))

    @Mail.send_exception_info_to_admin_emails
    def _listreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["listreminder"].run(["listreminder"] + context.args, TelegramExecutionContext(update))
