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


def escape_markdown_text(text: str):
    return (
        text
        .replace('_', '\\_')
        .replace('*', '\\*')
        .replace('[', '\\[')
        .replace(']', '\\]')
        .replace('(', '\\(')
        .replace(')', '\\)')
        .replace('~', '\\~')
        .replace('`', '\\`')
        .replace('>', '\\>')
        .replace('#', '\\#')
        .replace('+', '\\+')
        .replace('-', '\\-')
        .replace('=', '\\=')
        .replace('|', '\\|')
        .replace('{', '\\{')
        .replace('}', '\\}')
        .replace('.', '\\.')
        .replace('!', '\\!')
    )


def reply(update: Update, text: str, disable_web_page_preview: bool = False) -> None:
    text = escape_markdown_text(text)
    reply_message = update.message.reply_text(
        text, parse_mode="MarkdownV2",
        disable_web_page_preview=disable_web_page_preview,
    )
    title = reply_message.chat.title or "<DM>"
    log.info(f"({title}) {reply_message.from_user.username}: {reply_message.text}")
