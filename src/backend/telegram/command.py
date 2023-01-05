import asyncio
import functools

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Dispatcher

from src.api.command import Command, CommandBinding, SupportedPlatforms
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


def add_handler(dispatcher: Dispatcher, command: Command) -> None:
    bc.telegram.handlers[command.command_name] = CommandHandler(
        command.command_name,
        functools.partial(command_handler, command.command_name), run_async=True)
    dispatcher.add_handler(bc.telegram.handlers[command.command_name])


def remove_handler(dispatcher: Dispatcher, cmd_name: str) -> None:
    if cmd_name in bc.telegram.handlers.keys():
        dispatcher.remove_handler(bc.telegram.handlers[cmd_name])


class TelegramCommandBinding(CommandBinding):
    def __init__(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher

    def bind(self, cmd_name: str, command: Command):
        if not (command.supported_platforms & SupportedPlatforms.TELEGRAM):
            return
        add_handler(self._dispatcher, command)

    def unbind(self, cmd_name: str):
        remove_handler(self._dispatcher, cmd_name)
