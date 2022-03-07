from telegram import Update

from src.config import bc
from src.log import log


def log_command(update: Update):
    title = update.message.chat.title or "<DM>"
    log.info("(" + title + ") " + update.message.from_user.username + ": " + update.message.text)


def check_auth(update: Update) -> bool:
    if update.message.chat.id not in bc.config.telegram["channel_whitelist"]:
        return False
    return True
