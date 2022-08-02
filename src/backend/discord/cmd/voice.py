"""Connection to voice channel"""

import asyncio
import datetime
import os
import urllib.parse

import yt_dlp

from src import const
from src.backend.discord.embed import DiscordEmbed
from src.backend.discord.message import Msg
from src.backend.discord.voice import VoiceQueueEntry
from src.commands import BaseCmd
from src.config import bc
from src.log import log
from src.utils import Util, null


class _VoiceInternals:
    @staticmethod
    async def push_video(message, yt_video_url, silent):
        """Push video by its URL to voice queue"""
        r = const.YT_VIDEO_REGEX.match(yt_video_url)
        if r is None:
            return
        yt_video_id = r.groups()[0]
        output_file_name = f'{Util.tmp_dir()}/yt_{yt_video_id}.mp3'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_file_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                video_info = ydl.extract_info(yt_video_url, download=False)
                if not os.path.exists(output_file_name):
                    log.debug(f"Downloading YT video {yt_video_url} ...")
                    await Msg.response(message, f"Downloading YT video {yt_video_url} ...", silent)
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, ydl.download, [yt_video_url])
                    log.debug(f"Downloaded {yt_video_url}")
                else:
                    log.debug(f"Found in cache: {yt_video_url}")
        except Exception as e:
            return null(await Msg.response(message, f"🔊 ERROR: Downloading failed: {e}", silent))
        bc.voice_ctx.queue.append(VoiceQueueEntry(
            message.channel, video_info['title'], video_info['id'], output_file_name, message.author.name))
        e = DiscordEmbed()
        e.title(f"🔊 Added to queue '{video_info['title']}' at position {len(bc.voice_ctx.queue)}")
        e.title_url(video_info['webpage_url'])
        e.color(0xcc1818)
        e.thumbnail(video_info['thumbnail'])
        e.add_field("YouTube ID", video_info['id'], True)
        e.add_field("Duration", str(datetime.timedelta(seconds=video_info['duration'])), True)
        e.add_field("Uploader", video_info['uploader'], True)
        ud = video_info['upload_date']
        e.add_field("Upload date", f"{datetime.date(int(ud[0:4]), int(ud[4:6]), int(ud[6:8]))}", True)
        e.add_field("Views", video_info['view_count'], True)
        e.add_field("Likes", video_info['like_count'], True)
        await Msg.response(message, None, silent, embed=e.get())

    @staticmethod
    async def print_yt_info(message, video_url, silent, full_description=False):
        """Print YT video info in embed"""
        r = const.YT_VIDEO_REGEX.match(video_url)
        if r is None:
            return null(await Msg.response(message, "Please, provide valid YT link", silent))
        ydl_opts = {
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            return null(await Msg.response(message, f"ERROR: Getting YT video info failed: {e}", silent))
        ud = info['upload_date']
        e = DiscordEmbed()
        e.title(info['title'])
        e.title_url(info['webpage_url'])
        e.description(info['description'][:2048] if full_description else '')
        e.color(0xcc1818)
        e.thumbnail(info['thumbnail'])
        e.add_field("Views", str(info['view_count']), True)
        e.add_field("Likes", str(info['like_count']), True)
        e.add_field("Channel", f"[{info['uploader']}]({info['uploader_url']})", True)
        e.add_field("Uploaded", f"{datetime.date(int(ud[0:4]), int(ud[4:6]), int(ud[6:8]))}", True)
        e.add_field("Duration", f"{datetime.timedelta(seconds=info['duration'])}", True)
        await Msg.response(message, None, silent, embed=e.get())


class VoiceCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "vjoin": dict(permission=const.Permission.USER.value, subcommand=False),
            "vleave": dict(permission=const.Permission.USER.value, subcommand=False),
            "vqpush": dict(permission=const.Permission.USER.value, subcommand=False, max_execution_time=-1),
            "vqfpush": dict(permission=const.Permission.USER.value, subcommand=False, max_execution_time=-1),
            "vqcurrent": dict(permission=const.Permission.USER.value, subcommand=False),
            "vqskip": dict(permission=const.Permission.USER.value, subcommand=False),
            "vq": dict(permission=const.Permission.USER.value, subcommand=False),
            "ytinfo": dict(permission=const.Permission.USER.value, subcommand=False),
            "vqautorejoin": dict(permission=const.Permission.MOD.value, subcommand=False),
        })

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
                if bc.voice_ctx.client is not None:
                    log.debug("Disconnecting from previous voice channel...")
                    await bc.voice_ctx.client.disconnect()
                    log.debug("Disconnected from previous voice channel")
                    bc.voice_ctx.client = None
                log.debug(f"Connecting to the voice channel {voice_channel_id}...")
                try:
                    bc.voice_ctx.client = await v.connect()
                except Exception as e:
                    return null(await Msg.response(message, f"ERROR: Failed to connect: {e}", silent))
                log.debug("Connected to the voice channel")
                break
        else:
            await Msg.response(message, f"🔊 Could not find voice channel with id {voice_channel_id}", silent)

    @staticmethod
    async def _vleave(message, command, silent=False):
        """Leave (part) voice channel
    Usage: !vleave"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if bc.voice_ctx.client is not None:
            log.debug("Leaving previous voice channel...")
            await bc.voice_ctx.client.disconnect()
            log.debug("Left previous voice channel")
            bc.voice_ctx.client = None
        else:
            log.debug("No previous voice channel to leave")

    @staticmethod
    async def _vqpush(message, command, silent=False):
        """Push YT video or playlist to queue in voice channel
    Usage: !vqpush <youtube_url>"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        for i in range(1, len(command)):
            yt_url = command[i]
            r = const.YT_VIDEO_REGEX.match(yt_url) or const.YT_PLAYLIST_REGEX.match(yt_url)
            if r is None:
                return null(await Msg.response(message, "🔊 Please, provide YT link", silent))

            # Parse YT url
            parse_url = urllib.parse.urlparse(yt_url)
            params = urllib.parse.parse_qs(parse_url.query)

            if parse_url.path == '/playlist' and 'list' in params.keys() and params['list']:
                # Process YT playlist
                ydl_opts = {
                    'dump_single_json': True,
                    'extract_flat': True,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        yt_playlist_data = ydl.extract_info(yt_url, download=False)
                except Exception as e:
                    return null(await Msg.response(message, f"🔊 ERROR: Fetching YT playlist data failed: {e}", silent))
                yt_video_ids = [entry["id"] for entry in yt_playlist_data["entries"]]
                download_promises = []
                for yt_video_id in yt_video_ids:
                    download_promises.append(
                        _VoiceInternals.push_video(message, f"https://youtu.be/{yt_video_id}", silent))
                await asyncio.gather(*download_promises)
                await Msg.response(message, f"Downloading playlist '{params['list'][0]}' is finished", silent)
            else:
                # Process YT video
                await _VoiceInternals.push_video(message, yt_url, silent)

    @staticmethod
    async def _vqfpush(message, command, silent=False):
        """Find and push YT video
    Usage: !vqfpush <search query>"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        query = ' '.join(command[2:])
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        await _VoiceInternals.push_video(message, video_info['webpage_url'], silent)

    @staticmethod
    async def _vqcurrent(message, command, silent=False):
        """Show current video in queue
    Usage: !vqcurrent"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if bc.current_video is not None:
            video_url = f"https://youtu.be/{bc.current_video.id}"
            await _VoiceInternals.print_yt_info(message, video_url, silent)
        else:
            await Msg.response(message, "🔊 No current song", silent)

    @staticmethod
    async def _vqskip(message, command, silent=False):
        """Skip current track in voice queue
    Usage: !vqskip"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if bc.voice_ctx.client is not None:
            bc.voice_ctx.client.stop()
            await Msg.response(message, "Skipped current song", silent)
        else:
            log.debug("Nothing to skip")

    @staticmethod
    async def _vq(message, command, silent=False):
        """List voice channel queue
    Usage: !vq"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        if not bc.voice_ctx.queue:
            e = DiscordEmbed()
            e.title("🔊 Voice queue 🔊")
            e.color(0xcc1818)
            e.description("<empty>")
            return null(await Msg.response(message, None, silent, embed=e.get()))
        voice_ctx.queue = list(bc.voice_ctx.queue)
        pos = 0
        for voice_queue_chunk in Msg.split_by_chunks(voice_ctx.queue, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
            e = DiscordEmbed()
            e.title("🔊 Voice queue 🔊")
            e.color(0xcc1818)
            for entry in voice_queue_chunk:
                pos += 1
                e.add_field(
                    f"{entry.title}",
                    f"Position {pos} (YT: {entry.id}) requested by {entry.requested_by}"
                )
            await Msg.response(message, None, silent, embed=e.get())

    @staticmethod
    async def _ytinfo(message, command, silent=False):
        """Print info about YT video
    Usage:
        !ytinfo <youtube_url>
        !ytinfo <youtube_url> -f  <- full description"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        video_url = command[1]
        await _VoiceInternals.print_yt_info(
            message, video_url, silent, full_description=len(command) > 2 and command[2] == "-f")

    @staticmethod
    async def _vqautorejoin(message, command, silent=False):
        """Set/unset automatic rejoin to voice channel when queue is not empty
    Usage:
        !vqautorejoin <voice_channel_id>  <- set
        !vqautorejoin                     <- unset"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 1:
            if bc.voice_ctx.auto_rejoin_channel is not None:
                bc.voice_ctx.client.auto_rejoin = False
                await Msg.response(message, "Automatic rejoin is disabled", silent)
            else:
                await Msg.response(message, "Automatic rejoin is not set", silent)
            return
        voice_channel_id = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an id of voice channel", silent)
        if voice_channel_id is None:
            return
        voice_channels = message.guild.voice_channels
        for v in voice_channels:
            if v.id == voice_channel_id:
                bc.voice_ctx.auto_rejoin_channel = v
                await Msg.response(message, f"Automatic rejoin is enabled to {v.name}", silent)
                return
        else:
            return null(await Msg.response(message, f"Voice channel with id {voice_channel_id} is not found", silent))
