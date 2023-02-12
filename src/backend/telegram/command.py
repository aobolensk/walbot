import functools

from telegram import Update
from telegram.ext import Application, CallbackContext, CommandHandler

from src.api.command import Command, CommandBinding, SupportedPlatforms
from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_message
from src.config import bc
from src.mail import Mail
from src.message_cache import CachedMsg


async def _command_handler(command_name: str, update: Update, context: CallbackContext) -> None:
    await bc.executor.commands[command_name].run(
        [command_name] + context.args, TelegramExecutionContext(update, context))


@Mail.send_exception_info_to_admin_emails
async def command_handler(command_name: str, update: Update, context: CallbackContext) -> None:
    text = update.message.text
    log_message(update)
    # 'authorize' and 'resetpass' commands should be available for all channels to authorize bot there
    if command_name not in ("authorize", "resetpass") and not check_auth(update):
        return
    bc.message_cache.push(str(update.message.chat.id), CachedMsg(text, str(update.message.from_user.id)))
    await _command_handler(command_name, update, context)


def add_handler(app: Application, command: Command) -> None:
    bc.telegram.handlers[command.command_name] = CommandHandler(
        command.command_name,
        functools.partial(command_handler, command.command_name))
    app.add_handler(bc.telegram.handlers[command.command_name])


def remove_handler(app: Application, cmd_name: str) -> None:
    if cmd_name in bc.telegram.handlers.keys():
        app.remove_handler(bc.telegram.handlers[cmd_name])


class TelegramCommandBinding(CommandBinding):
    def __init__(self, app: Application) -> None:
        self._app = app

    def bind(self, cmd_name: str, command: Command):
        if not (command.supported_platforms & SupportedPlatforms.TELEGRAM):
            return
        add_handler(self._app, command)

    def unbind(self, cmd_name: str):
        remove_handler(self._app, cmd_name)
