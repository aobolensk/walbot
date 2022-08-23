import functools

from telegram.ext import CommandHandler

from src.backend.telegram.command import command_handler


class ReminderCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("reminder", functools.partial(command_handler, "reminder")))
        dispatcher.add_handler(CommandHandler("addreminder", functools.partial(command_handler, "addreminder")))
        dispatcher.add_handler(CommandHandler("updreminder", functools.partial(command_handler, "updreminder")))
        dispatcher.add_handler(CommandHandler("listreminder", functools.partial(command_handler, "listreminder")))
        dispatcher.add_handler(CommandHandler("delreminder", functools.partial(command_handler, "delreminder")))
        dispatcher.add_handler(CommandHandler("remindme", functools.partial(command_handler, "remindme")))
        dispatcher.add_handler(CommandHandler("remindwme", functools.partial(command_handler, "remindwme")))
        dispatcher.add_handler(CommandHandler("remindeme", functools.partial(command_handler, "remindeme")))
        dispatcher.add_handler(CommandHandler("repeatreminder", functools.partial(command_handler, "repeatreminder")))
        dispatcher.add_handler(CommandHandler("skipreminder", functools.partial(command_handler, "skipreminder")))
        dispatcher.add_handler(CommandHandler(
            "timeuntilreminder", functools.partial(command_handler, "timeuntilreminder")))
        dispatcher.add_handler(CommandHandler(
            "setprereminders", functools.partial(command_handler, "setprereminders")))
        dispatcher.add_handler(CommandHandler(
            "addremindernotes", functools.partial(command_handler, "addremindernotes")))
        dispatcher.add_handler(CommandHandler(
            "setreminderchannel", functools.partial(command_handler, "setreminderchannel")))
