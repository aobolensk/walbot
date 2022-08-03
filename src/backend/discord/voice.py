import asyncio
from dataclasses import dataclass

import discord

from src.backend.discord.embed import DiscordEmbed
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log
from src.mail import Mail


@dataclass
class VoiceQueueEntry:
    channel: discord.TextChannel
    title: str
    id: str
    file_name: str
    requested_by: str


class VoiceRoutine:
    def __init__(self, bot_cache) -> None:
        self.bot_cache = bot_cache
        self._voice_client_queue_disconnect_counter = 0
        bc.voice_ctx.current_video = None

    async def _update_autoupdate_flag(self, current_autoupdate_flag: bool) -> None:
        if current_autoupdate_flag != self.bot_cache.get_state()["do_not_update"]:
            self.bot_cache.update({"do_not_update": current_autoupdate_flag})
            self.bot_cache.dump_to_file()

    @Mail.send_exception_info_to_admin_emails_async
    async def _iteration(self) -> None:
        if bc.voice_ctx.client is not None and not bc.voice_ctx.queue and not bc.voice_ctx.client.is_playing():
            if bc.voice_ctx.current_video is not None:
                bc.voice_ctx.current_video = None
            self._voice_client_queue_disconnect_counter += 1
            if self._voice_client_queue_disconnect_counter >= 10:
                log.debug("Queue is empty. Disconnecting...")
                await bc.voice_ctx.client.disconnect()
                log.debug("Disconnected due to empty queue")
                bc.voice_ctx.client = None
                self._voice_client_queue_disconnect_counter = 0
                return
        else:
            self._voice_client_queue_disconnect_counter = 0
        if bc.voice_ctx.client is None and bc.voice_ctx.queue and bc.voice_ctx.auto_rejoin_channel is not None:
            log.debug("Joining saved voice channel...")
            bc.voice_ctx.client = await bc.voice_ctx.auto_rejoin_channel.connect()
            log.debug("Automatically joined saved voice channel")
            return
        if bc.voice_ctx.client is None or not bc.voice_ctx.queue or bc.voice_ctx.client.is_playing():
            return
        if not bc.voice_ctx.client.is_connected():
            log.debug("Connecting voice channel (1/2)...")
            try:
                await bc.voice_ctx.client.connect()
            except Exception as e:
                log.error(f"Failed to connect: {e}")
            log.debug("Connecting voice channel (2/2)...")
        if not bc.voice_ctx.client.is_playing():
            entry = bc.voice_ctx.queue.popleft()
            bc.voice_ctx.current_video = entry
            try:
                log.debug(f"Started to play {entry.file_name}")
                bc.voice_ctx.client.play(discord.FFmpegPCMAudio(entry.file_name))
            except Exception as e:
                await entry.channel.send(f"ERROR: Failed to play: {e}")
            e = DiscordEmbed()
            e.title(f"🔊 Now playing: {entry.title} (YT: {entry.id}) requested by {entry.requested_by}")
            e.color(0xcc1818)
            await entry.channel.send(None, embed=e.get())

    async def start(self) -> None:
        # Disconnect if bot is inactive in voice channel
        while True:
            bc.do_not_update[DoNotUpdateFlag.VOICE] = bool(bc.voice_ctx.client)
            await self._update_autoupdate_flag(any(bc.do_not_update))
            await self._iteration()
            await asyncio.sleep(5)
