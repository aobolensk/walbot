import asyncio
from dataclasses import dataclass

import discord

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
        bc.current_video = None

    async def _update_autoupdate_flag(self, current_autoupdate_flag: bool) -> None:
        if current_autoupdate_flag != self.bot_cache.get_state()["do_not_update"]:
            self.bot_cache.update({"do_not_update": current_autoupdate_flag})
            self.bot_cache.dump_to_file()

    async def start(self) -> None:
        # Disconnect if bot is inactive in voice channel

        @Mail.send_exception_info_to_admin_emails_async
        async def iteration():
            if bc.voice_client is not None and not bc.voice_client_queue and not bc.voice_client.is_playing():
                if bc.current_video is not None:
                    bc.current_video = None
                self._voice_client_queue_disconnect_counter += 1
                if self._voice_client_queue_disconnect_counter >= 10:
                    log.debug("Queue is empty. Disconnecting...")
                    await bc.voice_client.disconnect()
                    log.debug("Disconnected due to empty queue")
                    bc.voice_client = None
                    self._voice_client_queue_disconnect_counter = 0
                    return
            else:
                self._voice_client_queue_disconnect_counter = 0
            if bc.voice_client is None or not bc.voice_client_queue or bc.voice_client.is_playing():
                return
            if not bc.voice_client.is_connected():
                log.debug("Connecting voice channel (1/2)...")
                try:
                    await bc.voice_client.connect()
                except Exception as e:
                    log.error(f"Failed to connect: {e}")
                log.debug("Connecting voice channel (1/2)...")
            if not bc.voice_client.is_playing():
                entry = bc.voice_client_queue.popleft()
                bc.current_video = entry
                try:
                    log.debug(f"Started to play {entry.file_name}")
                    bc.voice_client.play(discord.FFmpegPCMAudio(entry.file_name))
                except Exception as e:
                    await entry.channel.send(f"ERROR: Failed to play: {e}")
                await entry.channel.send(
                    f"🔊 Now playing: {entry.title} (YT: {entry.id}) requested by {entry.requested_by}")

        while True:
            bc.do_not_update[DoNotUpdateFlag.VOICE] = bool(bc.voice_client)
            await self._update_autoupdate_flag(any(bc.do_not_update))
            await iteration()
            await asyncio.sleep(5)