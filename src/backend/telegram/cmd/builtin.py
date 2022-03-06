from src.config import bc
from src.mail import Mail

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("ping", self._ping))
        dispatcher.add_handler(CommandHandler("markov", self._markov))
        dispatcher.add_handler(CommandHandler("about", self._about))
        dispatcher.add_handler(CommandHandler("poll", self._poll))

    @Mail.send_exception_info_to_admin_emails
    def _ping(self, update: Update, context: CallbackContext):
        update.message.reply_text('Pong!')

    @Mail.send_exception_info_to_admin_emails
    def _markov(self, update: Update, context: CallbackContext):
        result = bc.markov.generate()
        update.message.reply_text(result)

    @Mail.send_exception_info_to_admin_emails
    def _about(self, update: Update, context: CallbackContext):
        cmd_txt = context.args[0] if context.args else ""
        verbosity = 0
        if cmd_txt == "-v":
            verbosity = 1
        elif cmd_txt == "-vv":
            verbosity = 2
        update.message.reply_text(bc.info.get_full_info(verbosity))

    @Mail.send_exception_info_to_admin_emails
    def _poll(self, update: Update, context: CallbackContext):
        if len(context.args) < 2:
            update.message.reply_text("Usage: /poll option 1;option 2;option 3")
            return
        options = ' '.join(context.args).split(';')
        context.bot.send_poll(
            update.effective_chat.id,
            "Poll",
            options,
        )
