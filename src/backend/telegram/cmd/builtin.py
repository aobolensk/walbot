from src.config import bc

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


class BuiltinCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("ping", self._ping))
        dispatcher.add_handler(CommandHandler("markov", self._markov))
        dispatcher.add_handler(CommandHandler("listreminder", self._listreminder))
        dispatcher.add_handler(CommandHandler("about", self._about))

    def _ping(self, update: Update, context: CallbackContext):
        update.message.reply_text('Pong!')

    def _markov(self, update: Update, context: CallbackContext):
        result = bc.markov.generate()
        update.message.reply_text(result)

    def _listreminder(self, update: Update, context: CallbackContext):
        reminder_list = []
        for index, reminder in bc.config.reminders.items():
            rep = f' (repeats every {reminder.repeat_after} {reminder.repeat_interval_measure})'
            prereminders = f' ({", ".join([str(x) + " min" for x in reminder.prereminders_list])} prereminders enabled)'
            reminder_list.append(
                (reminder.time,
                 reminder.message,
                 f"{index} at {reminder.time} "
                 f" in <#{reminder.channel_id}> (Discord)'"
                 f"{rep if reminder.repeat_after else ''}"
                 f"{prereminders if reminder.prereminders_list else ''}"))
        reminder_list.sort()
        result = ""
        for reminder in reminder_list:
            result += f"{reminder[0]}: {reminder[1]} {reminder[2]}\n"
        update.message.reply_text(result if result else "No reminders")

    def _about(self, update: Update, context: CallbackContext):
        cmd_txt = context.args[0] if context.args else ""
        verbosity = 0
        if cmd_txt == "-v":
            verbosity = 1
        elif cmd_txt == "-vv":
            verbosity = 2
        update.message.reply_text(bc.info.get_full_info(verbosity))
        raise Exception("123")
