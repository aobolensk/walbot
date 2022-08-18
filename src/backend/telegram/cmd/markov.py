from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.backend.telegram.context import TelegramExecutionContext
from src.backend.telegram.util import check_auth, log_command
from src.config import bc
from src.mail import Mail


class MarkovCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("markov", self._markov))
        dispatcher.add_handler(CommandHandler("markovgc", self._markovgc))
        dispatcher.add_handler(CommandHandler("delmarkov", self._delmarkov))
        dispatcher.add_handler(CommandHandler("findmarkov", self._findmarkov))
        dispatcher.add_handler(CommandHandler("getmarkovword", self._getmarkovword))

    @Mail.send_exception_info_to_admin_emails
    def _markov(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["markov"].run(["markov"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _markovgc(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["markovgc"].run(["markovgc"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _delmarkov(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["delmarkov"].run(["delmarkov"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _findmarkov(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["findmarkov"].run(["findmarkov"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _getmarkovword(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["getmarkovword"].run(["getmarkovword"] + context.args, TelegramExecutionContext(update))
