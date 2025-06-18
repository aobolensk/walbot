import asyncio
import datetime
import os
import urllib.parse
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List

import browser_cookie3  # type:ignore
import discord
import yt_dlp  # type:ignore

from src import const
from src.api.command import BaseCmd, Command, SupportedPlatforms
from src.api.execution_context import ExecutionContext
from src.api.plugin import BasePlugin
from src.backend.discord.embed import DiscordEmbed
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log
from src.mail import Mail
from src.utils import Util


class VoiceCtx:
    def __init__(self):
        self.client = None
        self.queue = deque()
        self.auto_rejoin_channel = None
        self.current_video = None
        self.cookies = browser_cookie3.firefox(domain_name="youtube.com")


@dataclass
class VoiceQueueEntry:
    channel: discord.TextChannel
    title: str
    id: str
    file_name: str
    requested_by: str


class _VoiceInternals:
    @staticmethod
    async def push_video(execution_ctx: ExecutionContext, yt_video_url: str, voice_ctx: VoiceCtx):
        """Push video by its URL to voice queue"""
        r = const.YT_VIDEO_REGEX.match(yt_video_url)
        if r is None:
            return
        yt_video_id = r.groups()[0]
        output_file_name = f'{Util.tmp_dir()}/yt_{yt_video_id}.mp3'
        ydl_opts = {
            'cookiejar': voice_ctx.cookies,
            'format': 'bestaudio/best',
            'outtmpl': output_file_name,
            'keepvideo': True,
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
                    await Command.send_message(execution_ctx, f"Downloading YT video {yt_video_url} ...")
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, ydl.download, [yt_video_url])
                    log.debug(f"Downloaded {yt_video_url}")
                else:
                    log.debug(f"Found in cache: {yt_video_url}")
        except Exception as e:
            return await Command.send_message(execution_ctx, f"🔊 ERROR: Downloading failed: {e}")
        voice_ctx.queue.append(VoiceQueueEntry(
            execution_ctx.message.channel, video_info['title'],
            video_info['id'], output_file_name, execution_ctx.message_author()))
        e = DiscordEmbed()
        e.title(f"🔊 Added to queue '{video_info['title']}' at position {len(voice_ctx.queue)}")
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
        await Command.send_message(execution_ctx, None, embed=e.get())

    @staticmethod
    async def print_yt_info(execution_ctx: ExecutionContext, video_url: str, full_description: bool = False):
        """Print YT video info in embed"""
        r = const.YT_VIDEO_REGEX.match(video_url)
        if r is None:
            return await Command.send_message(execution_ctx, "Please, provide valid YT link")
        ydl_opts: Dict[Any, Any] = {
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
        except Exception as e:
            return await Command.send_message(execution_ctx, f"ERROR: Getting YT video info failed: {e}")
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
        await Command.send_message(execution_ctx, None, embed=e.get())


class DiscordVideoQueuePluginCommands(BaseCmd):
    def __init__(self, voice_ctx: VoiceCtx) -> None:
        self._voice_ctx = voice_ctx

    async def register_commands(self) -> None:
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vjoin", const.Permission.USER, self._vjoin,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vleave", const.Permission.USER, self._vleave,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vqpush", const.Permission.USER, self._vqpush, max_execution_time=-1,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vqfpush", const.Permission.USER, self._vqfpush, max_execution_time=-1,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vqcurrent", const.Permission.USER, self._vqcurrent,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vqskip", const.Permission.USER, self._vqskip,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vq", const.Permission.USER, self._vq,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "ytinfo", const.Permission.USER, self._ytinfo,
            supported_platforms=SupportedPlatforms.DISCORD)
        await bc.plugin_manager.register_bot_command(
            self.get_classname(), "vqautorejoin", const.Permission.MOD, self._vqautorejoin,
            supported_platforms=SupportedPlatforms.DISCORD)

    async def unregister_commands(self) -> None:
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vjoin")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vleave")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vqpush")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vqfpush")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vqcurrent")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vqskip")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vq")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "ytinfo")
        await bc.plugin_manager.unregister_bot_command(self.get_classname(), "vqautorejoin")

    async def _vjoin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Join voice channel
    Usage: !vjoin <voice_channel_id>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        voice_channel_id = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an id of voice channel")
        if voice_channel_id is None:
            return
        voice_channels = execution_ctx.message.guild.voice_channels
        for v in voice_channels:
            if v.id == voice_channel_id:
                if self._voice_ctx.client is not None:
                    log.debug("Disconnecting from previous voice channel...")
                    await self._voice_ctx.client.disconnect()
                    log.debug("Disconnected from previous voice channel")
                    self._voice_ctx.client = None
                log.debug(f"Connecting to the voice channel {voice_channel_id}...")
                try:
                    self._voice_ctx.client = await v.connect()
                except Exception as e:
                    return await Command.send_message(execution_ctx, f"ERROR: Failed to connect: {e}")
                log.debug("Connected to the voice channel")
                break
        else:
            await Command.send_message(execution_ctx, f"🔊 Could not find voice channel with id {voice_channel_id}")

    async def _vleave(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Leave (part) voice channel
    Usage: !vleave"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        if self._voice_ctx.client is not None:
            log.debug("Leaving previous voice channel...")
            await self._voice_ctx.client.disconnect()
            log.debug("Left previous voice channel")
            self._voice_ctx.client = None
        else:
            log.debug("No previous voice channel to leave")

    async def _vqpush(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Push YT video or playlist to queue in voice channel
    Usage: !vqpush <youtube_url>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        for i in range(1, len(cmd_line)):
            yt_url = cmd_line[i]
            r = const.YT_VIDEO_REGEX.match(yt_url) or const.YT_PLAYLIST_REGEX.match(yt_url)
            if r is None:
                return await Command.send_message(execution_ctx, "🔊 Please, provide YT link")

            # Parse YT url
            parse_url = urllib.parse.urlparse(yt_url)
            params = urllib.parse.parse_qs(parse_url.query)

            if parse_url.path == '/playlist' and 'list' in params.keys() and params['list']:
                # Process YT playlist
                ydl_opts = {
                    'cookiejar': self._voice_ctx.cookies,
                    'dump_single_json': True,
                    'extract_flat': True,
                }
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        yt_playlist_data = ydl.extract_info(yt_url, download=False)
                except Exception as e:
                    return await Command.send_message(execution_ctx, f"🔊 ERROR: Fetching YT playlist data failed: {e}")
                yt_video_ids = [entry["id"] for entry in yt_playlist_data["entries"]]
                download_promises = []
                for yt_video_id in yt_video_ids:
                    download_promises.append(
                        _VoiceInternals.push_video(execution_ctx, f"https://youtu.be/{yt_video_id}", self._voice_ctx))
                await asyncio.gather(*download_promises)
                await Command.send_message(execution_ctx, f"Downloading playlist '{params['list'][0]}' is finished")
            else:
                # Process YT video
                await _VoiceInternals.push_video(execution_ctx, yt_url, self._voice_ctx)

    async def _vqfpush(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Find and push YT video
    Usage: !vqfpush <search query>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        query = ' '.join(cmd_line[2:])
        ydl_opts = {
            'cookiejar': self._voice_ctx.cookies,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            video_info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        await _VoiceInternals.push_video(execution_ctx, video_info['webpage_url'], self._voice_ctx)

    async def _vqcurrent(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Show current video in queue
    Usage: !vqcurrent"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        if self._voice_ctx.current_video is not None:
            video_url = f"https://youtu.be/{self._voice_ctx.current_video.id}"
            await _VoiceInternals.print_yt_info(execution_ctx, video_url)
        else:
            await Command.send_message(execution_ctx, "🔊 No current song")

    async def _vqskip(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Skip current track in voice queue
    Usage: !vqskip"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        if self._voice_ctx.client is not None:
            self._voice_ctx.client.stop()
            await Command.send_message(execution_ctx, "Skipped current song")
        else:
            log.debug("Nothing to skip")

    async def _vq(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """List voice channel queue
    Usage: !vq"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        if not self._voice_ctx.queue:
            e = DiscordEmbed()
            e.title("🔊 Voice queue 🔊")
            e.color(0xcc1818)
            e.description("<empty>")
            return await Command.send_message(execution_ctx, None, embed=e.get())
        voice_client_queue = list(self._voice_ctx.queue)
        pos = 0
        for voice_queue_chunk in Util.split_by_chunks(voice_client_queue, const.DISCORD_MAX_EMBED_FIELDS_COUNT):
            e = DiscordEmbed()
            e.title("🔊 Voice queue 🔊")
            e.color(0xcc1818)
            for entry in voice_queue_chunk:
                pos += 1
                e.add_field(
                    f"{entry.title}",
                    f"Position {pos} (YT: {entry.id}) requested by {entry.requested_by}"
                )
            await Command.send_message(execution_ctx, None, embed=e.get())

    async def _ytinfo(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print info about YT video
    Usage:
        !ytinfo <youtube_url>
        !ytinfo <youtube_url> -f  <- full description"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        video_url = cmd_line[1]
        await _VoiceInternals.print_yt_info(
            execution_ctx, video_url, full_description=len(cmd_line) > 2 and cmd_line[2] == "-f")

    async def _vqautorejoin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Set/unset automatic rejoin to voice channel when queue is not empty
    Usage:
        !vqautorejoin <voice_channel_id>  <- set
        !vqautorejoin                     <- unset"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=2):
            return
        if len(cmd_line) == 1:
            if self._voice_ctx.auto_rejoin_channel is not None:
                self._voice_ctx.client.auto_rejoin = False
                await Command.send_message(execution_ctx, "Automatic rejoin is disabled")
            else:
                await Command.send_message(execution_ctx, "Automatic rejoin is not set")
            return
        voice_channel_id = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an id of voice channel")
        if voice_channel_id is None:
            return
        voice_channels = execution_ctx.message.guild.voice_channels
        for v in voice_channels:
            if v.id == voice_channel_id:
                self._voice_ctx.auto_rejoin_channel = v
                await Command.send_message(execution_ctx, f"Automatic rejoin is enabled to {v.name}")
                return
        else:
            return await Command.send_message(execution_ctx, f"Voice channel with id {voice_channel_id} is not found")


class DiscordVideoQueuePlugin(BasePlugin):
    def __init__(self) -> None:
        super().__init__()
        self._voice_client_queue_disconnect_counter = 0
        self._voice_ctx = VoiceCtx()
        self._plugin_commands = DiscordVideoQueuePluginCommands(self._voice_ctx)

    async def init(self) -> None:
        await super().init()
        bc.discord.background_loop.create_task(self._start())
        await self._plugin_commands.register_commands()

    async def on_message(self, execution_ctx: ExecutionContext) -> None:
        # BasePlugin.on_message is abstract and has no implementation,
        # so calling super() here is unnecessary and triggers mypy's
        # "safe-super" check.  We simply implement an empty handler.
        return

    async def close(self) -> None:
        await super().close()
        await self._plugin_commands.unregister_commands()

    @Mail.send_exception_info_to_admin_emails
    async def _iteration(self) -> None:
        if self._voice_ctx.client is not None and not self._voice_ctx.queue and not self._voice_ctx.client.is_playing():
            if self._voice_ctx.current_video is not None:
                self._voice_ctx.current_video = None
            self._voice_client_queue_disconnect_counter += 1
            if self._voice_client_queue_disconnect_counter >= 10:
                log.debug("Queue is empty. Disconnecting...")
                await self._voice_ctx.client.disconnect()
                log.debug("Disconnected due to empty queue")
                self._voice_ctx.client = None
                self._voice_client_queue_disconnect_counter = 0
                return
        else:
            self._voice_client_queue_disconnect_counter = 0
        if self._voice_ctx.client is None and self._voice_ctx.queue and self._voice_ctx.auto_rejoin_channel is not None:
            log.debug("Joining saved voice channel...")
            self._voice_ctx.client = await self._voice_ctx.auto_rejoin_channel.connect()
            log.debug("Automatically joined saved voice channel")
            return
        if self._voice_ctx.client is None or not self._voice_ctx.queue or self._voice_ctx.client.is_playing():
            return
        if not self._voice_ctx.client.is_connected():
            log.debug("Connecting voice channel (1/2)...")
            try:
                await self._voice_ctx.client.connect()
            except Exception as e:
                log.error(f"Failed to connect: {e}")
            log.debug("Connecting voice channel (2/2)...")
        if not self._voice_ctx.client.is_playing():
            entry = self._voice_ctx.queue.popleft()
            self._voice_ctx.current_video = entry
            try:
                log.debug(f"Started to play {entry.file_name}")
                self._voice_ctx.client.play(discord.FFmpegPCMAudio(entry.file_name))
            except Exception as e:
                await entry.channel.send(f"ERROR: Failed to play: {e}")
            e = DiscordEmbed()
            e.title(f"🔊 Now playing: {entry.title} (YT: {entry.id}) requested by {entry.requested_by}")
            e.color(0xcc1818)
            await entry.channel.send(None, embed=e.get())

    async def _start(self) -> None:
        # Disconnect if bot is inactive in voice channel
        while True:
            bc.do_not_update[DoNotUpdateFlag.BUILTIN_PLUGIN_VQ] = bool(self._voice_ctx.client)
            await self._iteration()
            await asyncio.sleep(5)
