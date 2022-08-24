import functools

from telegram import update
from telegram.ext import CallbackContext, CommandHandler

from src.backend.telegram.command import command_handler
from src.backend.telegram.util import check_auth, log_command, reply
from src.mail import Mail


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("ping", functools.partial(command_handler, "ping")))
        dispatcher.add_handler(CommandHandler("echo", functools.partial(command_handler, "echo")))
        dispatcher.add_handler(CommandHandler("about", functools.partial(command_handler, "about")))
        dispatcher.add_handler(CommandHandler("shutdown", functools.partial(command_handler, "shutdown")))
        dispatcher.add_handler(CommandHandler("restart", functools.partial(command_handler, "restart")))
        dispatcher.add_handler(CommandHandler("uptime", functools.partial(command_handler, "uptime")))
        dispatcher.add_handler(CommandHandler("version", functools.partial(command_handler, "version")))
        dispatcher.add_handler(CommandHandler("curl", functools.partial(command_handler, "curl")))
        dispatcher.add_handler(CommandHandler("extexec", functools.partial(command_handler, "extexec")))
        dispatcher.add_handler(CommandHandler(
            "donotupdatestate", functools.partial(command_handler, "donotupdatestate")))
        dispatcher.add_handler(CommandHandler("getmentioncmd", functools.partial(command_handler, "getmentioncmd")))
        dispatcher.add_handler(CommandHandler("setmentioncmd", functools.partial(command_handler, "setmentioncmd")))
        dispatcher.add_handler(CommandHandler("poll", self._poll))

    @Mail.send_exception_info_to_admin_emails
    def _poll(self, update: update, context: CallbackContext) -> None:
        log_command(update)
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
