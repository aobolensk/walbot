import asyncio
from dataclasses import dataclass

import discord

from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log


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

    async def _update_autoupdate_flag(self, current_autoupdate_flag: bool) -> None:
        if current_autoupdate_flag != self.bot_cache.get_state()["do_not_update"]:
            self.bot_cache.update({"do_not_update": current_autoupdate_flag})
            self.bot_cache.dump_to_file()

    async def start(self) -> None:
        # Disconnect if bot is inactive in voice channel
        voice_client_queue_disconnect_counter = 0

        while True:
            bc.do_not_update[DoNotUpdateFlag.VOICE] = bool(bc.voice_client)
            await self._update_autoupdate_flag(any(bc.do_not_update))
            try:
                if bc.voice_client is not None and not bc.voice_client_queue and not bc.voice_client.is_playing():
                    voice_client_queue_disconnect_counter += 1
                    if voice_client_queue_disconnect_counter >= 10:
                        log.debug("Queue is empty. Disconnecting...")
                        await bc.voice_client.disconnect()
                        log.debug("Disconnected due to empty queue")
                        bc.voice_client = None
                        voice_client_queue_disconnect_counter = 0
                        continue
                else:
                    voice_client_queue_disconnect_counter = 0
                if bc.voice_client is None or not bc.voice_client_queue or bc.voice_client.is_playing():
                    await asyncio.sleep(5)
                    continue
                if not bc.voice_client.is_connected():
                    log.debug("Connecting voice channel (1/2)...")
                    try:
                        await bc.voice_client.connect()
                    except Exception as e:
                        log.error(f"Failed to connect: {e}")
                    log.debug("Connecting voice channel (1/2)...")
                if not bc.voice_client.is_playing():
                    entry = bc.voice_client_queue.popleft()
                    try:
                        log.debug(f"Started to play {entry.file_name}")
                        bc.voice_client.play(discord.FFmpegPCMAudio(entry.file_name))
                    except Exception as e:
                        await entry.channel.send(f"ERROR: Failed to play: {e}")
                    await entry.channel.send(
                        f"🔊 Now playing: {entry.title} (YT: {entry.id}) requested by {entry.requested_by}")
            except Exception as e:
                log.error(f"voice_routine logic failed: {e}")
            await asyncio.sleep(5)
