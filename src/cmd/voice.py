import uuid

import youtube_dl

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.utils import Util, null


class VoiceCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "vjoin",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vleave",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vqpush",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vq",
                                     permission=const.Permission.USER.value, subcommand=False)

    @staticmethod
    async def _vjoin(message, command, silent=False):
        """Join voice channel
    Usage: !vjoin <voice_channel_id>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        voice_channel_id = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an id of voice channel", silent)
        if voice_channel_id is None:
            return
        voice_channels = message.guild.voice_channels
        for v in voice_channels:
            if v.id == voice_channel_id:
                if bc.voice_client is not None:
                    await bc.voice_client.disconnect()
                    bc.voice_client = None
                bc.voice_client = await message.guild.voice_channels[0].connect()
                break
        else:
            await Msg.response(message, f"Could not find voice channel with id {voice_channel_id}", silent)

    @staticmethod
    async def _vleave(message, command, silent=False):
        """Leave (part) voice channel
    Usage: !vleave"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if bc.voice_client is not None:
            await bc.voice_client.disconnect()
            bc.voice_client = None

    @staticmethod
    async def _vqpush(message, command, silent=False):
        """Push YT video to queue in voice channel
    Usage: !vqpush <youtube_url>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if bc.voice_client is None:
            return null(await Msg.response(message, "Bot is not connected to voice channel", silent))
        output_file_name = f'/tmp/walbot/{uuid.uuid4().hex}.mp3'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        video_url = command[1]
        r = const.YT_VIDEO_REGEX.match(video_url)
        if r is None:
            return null(await Msg.response(message, "Please, provide YT link", silent))
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(video_url, download=False)
            ydl.download([video_url])
        bc.voice_client_queue.append((message.channel, video_info['title'], video_info['id'], output_file_name))
        await Msg.response(
            message,
            f"Added {video_info['title']} ({video_info['id']}) to the queue at position #{len(bc.voice_client_queue)}",
            silent)

    @staticmethod
    async def _vq(message, command, silent=False):
        """List voice channel queue
    Usage: !vq"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, entry in enumerate(bc.voice_client_queue):
            result += f"{index + 1}: {entry[1]} ({entry[2]})\n"
        await Msg.response(message, result, silent)
