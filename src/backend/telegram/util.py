from telegram import Update

from src.config import User, bc
from src.log import log


def log_message(update: Update) -> None:
    title = update.message.chat.title or "<DM>"
    log.info(f"({title}) {update.message.from_user.username}: {update.message.text}")


def check_auth(update: Update) -> bool:
    if update.message.chat.id not in bc.config.telegram.channel_whitelist:
        return False
    if update.message.from_user.id not in bc.config.telegram.users.keys():
        bc.config.telegram.users[update.message.from_user.id] = User(update.message.from_user.id)
    return True


def reply(update: Update, text: str) -> None:
    text = text.replace("-", "\\-").replace("!", "\\!")
    reply_message = update.message.reply_text(text, parse_mode="MarkdownV2")
    title = reply_message.chat.title or "<DM>"
    log.info(f"({title}) {reply_message.from_user.username}: {reply_message.text}")
