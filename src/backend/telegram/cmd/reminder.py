from src.config import bc
from src.mail import Mail
from src.backend.telegram.util import log_command

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


class ReminderCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("listreminder", self._listreminder))

    @Mail.send_exception_info_to_admin_emails
    def _listreminder(self, update: Update, context: CallbackContext):
        log_command(update)
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
