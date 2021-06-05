import datetime
import uuid

import discord
import youtube_dl

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.utils import Util, null
from src.voice import VoiceQueueEntry


class VoiceCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "vjoin",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vleave",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vqpush",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vqskip",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "vq",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "ytinfo",
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
                bc.voice_client = await v.connect()
                break
        else:
            await Msg.response(message, f"🔊 Could not find voice channel with id {voice_channel_id}", silent)

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
            return null(await Msg.response(message, "🔊 Please, provide YT link", silent))
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(video_url, download=False)
                ydl.download([video_url])
        except Exception as e:
            await Msg.response(message, f"🔊 ERROR: Downloading failed: {e}", silent)
        bc.voice_client_queue.append(VoiceQueueEntry(
            message.channel, video_info['title'], video_info['id'], output_file_name, message.author.name))
        await Msg.response(
            message,
            f"🔊 Added {video_info['title']} (YT: {video_info['id']}) to the queue "
            f"at position #{len(bc.voice_client_queue)}",
            silent)

    @staticmethod
    async def _vqskip(message, command, silent=False):
        """Skip current track in voice queue
    Usage: !vqskip"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if bc.voice_client is not None:
            bc.voice_client.stop()

    @staticmethod
    async def _vq(message, command, silent=False):
        """List voice channel queue
    Usage: !vq"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if not bc.voice_client_queue:
            return null(await Msg.response(message, "<Voice queue is empty>", silent))
        result = "🔊 Voice channel queue:\n"
        for index, entry in enumerate(bc.voice_client_queue):
            result += f"{index + 1}: {entry.title} (YT: {entry.id}) requested by {entry.requested_by}\n"
        await Msg.response(message, result, silent)

    @staticmethod
    async def _ytinfo(message, command, silent=False):
        """Print info about YT video
    Usage: !ytinfo <youtube_url>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        video_url = command[1]
        r = const.YT_VIDEO_REGEX.match(video_url)
        if r is None:
            return null(await Msg.response(message, "Please, provide valid YT link", silent))
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': "1.mp3",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            await Msg.response(message, f"ERROR: Getting YT video info failed: {e}", silent)
        ud = info['upload_date']
        yt_info_embed_dict = {
            "title": info['title'],
            "description": info['description'][:2048],
            "url": info['webpage_url'],
            "color": 0xcc1818,
            "thumbnail": {
                "url": info['thumbnail']
            },
            "fields": [
                { "name": "Likes", "value": f"{info['like_count']}", "inline": True },
                { "name": "Dislikes", "value": f"{info['dislike_count']}", "inline": True },
                { "name": "Channel", "value": f"[{info['uploader']}]({info['uploader_url']})", "inline": True },
                { "name": "Uploaded", "value": f"{datetime.date(int(ud[0:4]), int(ud[4:6]), int(ud[6:8]))}", "inline": True },
            ]
        }
        await Msg.response(message, "", silent, embed=discord.Embed.from_dict(yt_info_embed_dict))
