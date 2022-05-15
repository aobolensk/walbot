from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

from src.backend.telegram.util import check_auth, log_command, reply
from src.config import bc
from src.mail import Mail


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("ping", self._ping))
        dispatcher.add_handler(CommandHandler("markov", self._markov))
        dispatcher.add_handler(CommandHandler("about", self._about))
        dispatcher.add_handler(CommandHandler("poll", self._poll))

    @Mail.send_exception_info_to_admin_emails
    def _ping(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        reply(update, 'Pong!')

    @Mail.send_exception_info_to_admin_emails
    def _markov(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        result = bc.markov.generate()
        reply(update, result)

    @Mail.send_exception_info_to_admin_emails
    def _about(self, update: Update, context: CallbackContext) -> None:
        log_command(update)
        if not check_auth(update):
            return
        cmd_txt = context.args[0] if context.args else ""
        verbosity = 0
        if cmd_txt == "-v":
            verbosity = 1
        elif cmd_txt == "-vv":
            verbosity = 2
        reply(update, bc.info.get_full_info(verbosity))

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
