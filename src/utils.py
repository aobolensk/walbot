from . import const
from .config import Command
from .log import log


class Util:
    @staticmethod
    async def response(message, content, silent, **kwargs):
        if not silent:
            if content:
                for chunk in Command.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    await message.channel.send(chunk, tts=kwargs.get("tts", False))
            if kwargs.get("embed", None):
                await message.channel.send(embed=kwargs["embed"], tts=kwargs.get("tts", False))
        else:
            log.info("[SILENT] -> " + content)
