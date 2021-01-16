from src import const
from src.log import log


class Msg:
    @staticmethod
    def split_by_chunks(message, count):
        for i in range(0, len(message), count):
            yield message[i:i+count]

    @staticmethod
    async def reply(message, content, silent, **kwargs):
        if not silent:
            msg = None
            if content:
                for chunk in Msg.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await message.reply(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await message.reply(None, files=kwargs.get("files", None))
            if kwargs.get("embed", None):
                msg = await message.reply(embed=kwargs["embed"], tts=kwargs.get("tts", False))
                if kwargs.get("suppress_embeds", False):
                    await msg.edit(suppress=True)
            return msg
        else:
            log.info("[SILENT] -> " + content)

    @staticmethod
    async def response(message, content, silent, **kwargs):
        if not silent:
            msg = None
            if content:
                for chunk in Msg.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await message.channel.send(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await message.channel.send(None, files=kwargs.get("files", None))
            if kwargs.get("embed", None):
                msg = await message.channel.send(embed=kwargs["embed"], tts=kwargs.get("tts", False))
                if kwargs.get("suppress_embeds", False):
                    await msg.edit(suppress=True)
            return msg
        else:
            log.info("[SILENT] -> " + content)

    @staticmethod
    async def send_direct_message(author, content, silent, **kwargs):
        if not silent:
            if author.dm_channel is None:
                await author.create_dm()
            if content:
                for chunk in Msg.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await author.dm_channel.send(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await author.dm_channel.send(None, files=kwargs.get("files", None))
        else:
            log.info("[SILENT] -> " + content)
