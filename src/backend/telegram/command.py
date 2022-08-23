from telegram import Update
from telegram.ext import CallbackContext

from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_command
from src.config import bc
from src.mail import Mail


@Mail.send_exception_info_to_admin_emails
def command_handler(command_name: str, update: Update, context: CallbackContext) -> None:
    log_command(update)
    if not check_auth(update):
        return
    bc.executor.commands[command_name].run([command_name] + context.args, TelegramExecutionContext(update))
