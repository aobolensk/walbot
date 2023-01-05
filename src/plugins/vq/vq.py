import asyncio

import discord

from src.api.execution_context import ExecutionContext
from src.api.plugin import BasePlugin
from src.backend.discord.embed import DiscordEmbed
from src.bc import DoNotUpdateFlag
from src.config import bc
from src.log import log
from src.mail import Mail
from src.plugins.vq.cmd.vq_cmd import DiscordVideoQueuePluginCommands, VoiceCtx


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
        await super().on_message(execution_ctx)

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
