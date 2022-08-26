import functools

from telegram.ext import CommandHandler

from src.backend.telegram.command import command_handler


class MarkovCommands:
    def __init__(self) -> None:
        pass

    def add_handlers(self, dispatcher) -> None:
        dispatcher.add_handler(CommandHandler("markov", functools.partial(command_handler, "markov")))
        dispatcher.add_handler(CommandHandler("markovgc", functools.partial(command_handler, "markovgc")))
        dispatcher.add_handler(CommandHandler("delmarkov", functools.partial(command_handler, "delmarkov")))
        dispatcher.add_handler(CommandHandler("findmarkov", functools.partial(command_handler, "findmarkov")))
        dispatcher.add_handler(CommandHandler("getmarkovword", functools.partial(command_handler, "getmarkovword")))
        dispatcher.add_handler(CommandHandler("dropmarkov", functools.partial(command_handler, "dropmarkov")))
        dispatcher.add_handler(CommandHandler("statmarkov", functools.partial(command_handler, "statmarkov")))
        dispatcher.add_handler(CommandHandler("inspectmarkov", functools.partial(command_handler, "inspectmarkov")))
        dispatcher.add_handler(CommandHandler("addmarkovfilter", functools.partial(command_handler, "addmarkovfilter")))
        dispatcher.add_handler(CommandHandler("listmarkovfilter", functools.partial(command_handler, "listmarkovfilter")))
        dispatcher.add_handler(CommandHandler("delmarkovfilter", functools.partial(command_handler, "delmarkovfilter")))
