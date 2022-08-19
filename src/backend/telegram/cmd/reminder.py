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
        dispatcher.add_handler(CommandHandler("reminder", self._reminder))
        dispatcher.add_handler(CommandHandler("addreminder", self._addreminder))
        dispatcher.add_handler(CommandHandler("updreminder", self._updreminder))
        dispatcher.add_handler(CommandHandler("listreminder", self._listreminder))
        dispatcher.add_handler(CommandHandler("delreminder", self._delreminder))
        dispatcher.add_handler(CommandHandler("remindme", self._remindme))
        dispatcher.add_handler(CommandHandler("remindeme", self._remindeme))
        dispatcher.add_handler(CommandHandler("repeatreminder", self._repeatreminder))
        dispatcher.add_handler(CommandHandler("skipreminder", self._skipreminder))

    @Mail.send_exception_info_to_admin_emails
    def _reminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["reminder"].run(["reminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _addreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["addreminder"].run(["addreminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _updreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["updreminder"].run(["updreminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _listreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["listreminder"].run(["listreminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _delreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["delreminder"].run(["delreminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _remindme(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["remindme"].run(["remindme"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _remindeme(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["remindeme"].run(["remindeme"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _repeatreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["repeatreminder"].run(["repeatreminder"] + context.args, TelegramExecutionContext(update))

    @Mail.send_exception_info_to_admin_emails
    def _skipreminder(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        bc.executor.commands["skipreminder"].run(["skipreminder"] + context.args, TelegramExecutionContext(update))
