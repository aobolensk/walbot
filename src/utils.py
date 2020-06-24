from . import const
from .log import log


class Util:
    @staticmethod
    async def response(message, content, silent, **kwargs):
        if not silent:
            if content:
                for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
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
    async def send_direct_message(message, content, silent, **kwargs):
        if not silent:
            if message.author.dm_channel is None:
                await message.author.create_dm()
            if content:
                for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                    msg = await message.author.dm_channel.send(
                        chunk,
                        tts=kwargs.get("tts", False),
                        files=kwargs.get("files", None))
                    if kwargs.get("suppress_embeds", False):
                        await msg.edit(suppress=True)
            elif kwargs.get("files", None):
                msg = await message.author.dm_channel.send(None, files=kwargs.get("files", None))
        else:
            log.info("[SILENT] -> " + content)

    @staticmethod
    async def check_args_count(message, command, silent, min=None, max=None):
        if min and len(command) < min:
            await Util.response(message, "Too few arguments for command '{}'".format(command[0]), silent)
            return False
        if max and len(command) > max:
            await Util.response(message, "Too many arguments for command '{}'".format(command[0]), silent)
            return False
        return True

    @staticmethod
    def split_by_chunks(message, count):
        for i in range(0, len(message), count):
            yield message[i:i+count]

    @staticmethod
    async def parse_int(message, string, error_message, silent):
        try:
            return int(string)
        except ValueError:
            await Util.response(message, error_message, silent)
            return

    @staticmethod
    async def parse_float(message, string, error_message, silent):
        try:
            return float(string)
        except ValueError:
            await Util.response(message, error_message, silent)
            return
