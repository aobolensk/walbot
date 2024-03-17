from typing import Optional

import discord

from src import const
from src.log import log
from src.utils import Util


class Msg:
    @staticmethod
    async def reply(message, content, silent, **kwargs):
        """Reply on particular message"""
        if silent:
            return log.debug("[SILENT] -> " + content)
        msg = None
        if content:
            for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                if not chunk.strip():
                    continue
                msg = await message.reply(
                    chunk,
                    tts=kwargs.get("tts", False),
                    files=kwargs.get("files", None),
                    embed=kwargs.get("embed", None),
                    suppress=kwargs.get("suppress_embeds", False))
        elif kwargs.get("files", None):
            msg = await message.reply(None, files=kwargs.get("files", None))
        elif kwargs.get("embed", None):
            msg = await message.reply(
                embed=kwargs["embed"],
                tts=kwargs.get("tts", False),
                suppress=kwargs.get("suppress_embeds", False))
        return msg

    @staticmethod
    async def response(message, content, silent, **kwargs) -> Optional[discord.Message]:
        """Send response"""
        if silent:
            return log.debug("[SILENT] -> " + content)
        msg = None
        if content:
            for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                if not chunk.strip():
                    continue
                msg = await message.channel.send(
                    chunk,
                    tts=kwargs.get("tts", False),
                    view=kwargs.get("view", False),
                    files=kwargs.get("files", None),
                    embed=kwargs.get("embed", None),
                    suppress=kwargs.get("suppress_embeds", False))
        elif kwargs.get("files", None):
            msg = await message.channel.send(None, files=kwargs.get("files", None))
        elif kwargs.get("embed", None):
            msg = await message.channel.send(
                embed=kwargs["embed"],
                tts=kwargs.get("tts", False),
                suppress=kwargs.get("suppress_embeds", False))
        return msg

    @staticmethod
    async def send_direct_message(author, content, silent, **kwargs):
        """Send direct message to message author"""
        if silent:
            return log.debug("[SILENT] -> " + content)
        if author.dm_channel is None:
            await author.create_dm()
        msg = None
        if content:
            for chunk in Util.split_by_chunks(content, const.DISCORD_MAX_MESSAGE_LENGTH):
                if not chunk.strip():
                    continue
                msg = await author.dm_channel.send(
                    chunk,
                    tts=kwargs.get("tts", False),
                    files=kwargs.get("files", None),
                    embed=kwargs.get("embed", None),
                    suppress=kwargs.get("suppress_embeds", False))
        elif kwargs.get("files", None):
            msg = await author.dm_channel.send(None, files=kwargs.get("files", None))
        elif kwargs.get("embed", None):
            msg = await author.dm_channel.send(
                embed=kwargs["embed"],
                tts=kwargs.get("tts", False),
                suppress=kwargs.get("suppress_embeds", False))
        return msg
