from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_command, reply
from src.config import bc
from src.mail import Mail


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("ping", self._ping))
        dispatcher.add_handler(CommandHandler("about", self._about))
        dispatcher.add_handler(CommandHandler("poll", self._poll))
        dispatcher.add_handler(CommandHandler("uptime", self._uptime))
        dispatcher.add_handler(CommandHandler("version", self._version))
        dispatcher.add_handler(CommandHandler("curl", self._curl))
        dispatcher.add_handler(CommandHandler("donotupdatestate", self._donotupdatestate))
        dispatcher.add_handler(CommandHandler("getmentioncmd", self._getmentioncmd))
        dispatcher.add_handler(CommandHandler("setmentioncmd", self._setmentioncmd))

    @Mail.send_exception_info_to_admin_emails
    def _ping(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["ping"].run(["ping"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _about(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["about"].run(["about"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _poll(self, update: Update, context: CallbackContext) -> None:
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

    @Mail.send_exception_info_to_admin_emails
    def _uptime(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["uptime"].run(["uptime"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _version(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["version"].run(["version"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _curl(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["curl"].run(["curl"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _donotupdatestate(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["donotupdatestate"].run(
            ["donotupdatestate"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _getmentioncmd(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["getmentioncmd"].run(["getmentioncmd"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _setmentioncmd(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["setmentioncmd"].run(["setmentioncmd"] + context.args, TelegramExecutionContext(update))
