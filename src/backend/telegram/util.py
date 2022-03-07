from telegram import Update

from src.log import log


def log_command(update: Update):
    title = update.message.chat.title or "<DM>"
    log.info("(" + title + ") " + update.message.from_user.username + ": " + update.message.text)
