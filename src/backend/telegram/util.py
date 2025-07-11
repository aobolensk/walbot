from urllib.parse import quote_plus

from telegram import Update

from src.config import bc
from src.log import log
from src.utils import Util


def log_message(update: Update) -> None:
    title = update.message.chat.title or "<DM>"
    log.info(f"({title}) {update.message.from_user.username}: {update.message.text}")


def check_auth(update: Update) -> bool:
    if update.message.chat.id not in bc.config.telegram.channel_whitelist:
        return False
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


async def reply(update: Update, text: str, disable_web_page_preview: bool = False, reply_on_msg: bool = False) -> None:
    if not text:
        return
    if reply_on_msg:
        reply_message = await update.message.reply_text(
            text, parse_mode="MarkdownV2",
            disable_web_page_preview=disable_web_page_preview,
        )
    else:
        reply_message = await update.message.get_bot().send_message(
            update.message.chat_id,
            text, parse_mode="MarkdownV2",
            disable_web_page_preview=disable_web_page_preview,
        )
    title = reply_message.chat.title or "<DM>"
    log.info(f"({title}) {reply_message.from_user.username}: {reply_message.text}")


async def send_message(chat_id: int, text: str) -> None:
    log.info(f"({chat_id}) /sendMessage: " + text)
    text = quote_plus(escape_markdown_text(text))
    url = (
        f"https://api.telegram.org/bot{bc.secret_config.telegram['token']}/sendMessage"
        f"?chat_id={chat_id}&text={text}&parse_mode=MarkdownV2"
    )
    rq = Util.request(url)
    r = await rq.get()
    if r.status_code != 200:
        log.error(f"Error sending message to {chat_id}: {r.status_code} {r.json()}")
