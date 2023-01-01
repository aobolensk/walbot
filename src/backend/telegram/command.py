import asyncio

from telegram import Update
from telegram.ext import CallbackContext

from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_message
from src.config import bc
from src.mail import Mail
from src.message_cache import CachedMsg


async def _command_handler(command_name: str, update: Update, context: CallbackContext) -> None:
    await bc.executor.commands[command_name].run([command_name] + context.args, TelegramExecutionContext(update))


@Mail.send_exception_info_to_admin_emails
def command_handler(command_name: str, update: Update, context: CallbackContext) -> None:
    text = update.message.text
    log_message(update)
    if not check_auth(update):
        return
    bc.message_cache.push(str(update.message.chat.id), CachedMsg(text, str(update.message.from_user.id)))
    loop = asyncio.new_event_loop()
    loop.run_until_complete(_command_handler(command_name, update, context))
