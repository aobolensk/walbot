import asyncio
import datetime
import importlib
import itertools
import re
import sys
from typing import Any, Mapping, Optional, cast

import discord

from src import const
from src.algorithms import levenshtein_distance
from src.api.bot_instance import BotInstance
from src.backend.discord.commands import DiscordCommandBinding
from src.backend.discord.context import DiscordExecutionContext
from src.bot_cache import BotCache
from src.config import Config, GuildSettings, SecretConfig, User, bc
from src.ff import FF
from src.log import log
from src.mail import Mail
from src.message_cache import CachedMsg
from src.message_processing import MessageProcessing
from src.reminder import ReminderProcessing
from src.utils import Time, Util


class WalBot(discord.Client):
    def __init__(
            self, name: str, config: Config, secret_config: SecretConfig, intents: discord.Intents,
            fast_start: bool = False) -> None:
        http_proxy = Util.proxy.http()
        if http_proxy is not None:
            log.info("Discord instance is using proxy: " + http_proxy)
        super().__init__(intents=intents, proxy=http_proxy)
        self.repl = None
        self.instance_name = name
        self.config = config
        self.secret_config = secret_config
        self.bot_cache = BotCache(True)
        self.loop.create_task(self._process_reminders())
        self.loop.create_task(self._update_autoupdate_flag())
        bc.discord.commands = self.config.commands
        bc.discord.latency = lambda: self.latency
        bc.discord.change_status = self._change_status
        bc.discord.change_presence = self.change_presence
        bc.discord.get_channel = self.get_channel
        bc.discord.get_user = self.get_user
        bc.discord.background_loop = self.loop
        bc.executor.binders[const.BotBackend.DISCORD] = DiscordCommandBinding()
        if not fast_start:
            log.debug("Started Markov model checks...")
            if bc.markov.check():
                log.info("Markov model has passed all checks")
            else:
                log.info("Markov model has not passed checks, but all errors were fixed")

    async def _update_autoupdate_flag(self) -> None:
        if any(bc.do_not_update) != self.bot_cache.get_state()["do_not_update"]:
            self.bot_cache.update({"do_not_update": any(bc.do_not_update)})
            self.bot_cache.dump_to_file()

    async def _bot_runner_task(self, *args, **kwargs):
        try:
            await self.start(*args, **kwargs)
        finally:
            if not self.is_closed():
                await self.close()

    def run(self, *args, **kwargs):
        # Sightly patched implementation from discord.py discord.Client (parent) class
        # Reference: https://github.com/Rapptz/discord.py/blob/master/discord/client.py
        if sys.platform == "win32":
            return super().run(*args, **kwargs)
        loop = self.loop
        asyncio.ensure_future(self._bot_runner_task(*args, *kwargs), loop=loop)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            loop.stop()
            log.info('Received signal to terminate bot and event loop')
        log.info("Shutting down the bot...")
        tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}
        for task in tasks:
            task.cancel()
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        for task in tasks:
            if not task.cancelled():
                log.error("Asynchronous task cancel failed!")
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.run_until_complete(self._on_shutdown())
        loop.close()
        log.info("Bot is shut down!")

    async def _on_shutdown(self) -> None:
        if self.repl is not None:
            self.repl.stop()

    async def _change_status(self, string: str, type_: discord.ActivityType) -> None:
        await self.change_presence(activity=discord.Activity(name=string, type=type_))

    async def _config_autosave(self) -> None:
        await self.wait_until_ready()
        index = 1
        while not self.is_closed():
            await asyncio.sleep(self.config.saving["period"] * 60)
            if index % self.config.saving["backup"]["period"] == 0:
                self.config.backup(const.CONFIG_PATH, const.MARKOV_PATH)
            self.config.save(const.CONFIG_PATH, const.MARKOV_PATH, const.SECRET_CONFIG_PATH)
            index += 1

    @Mail.send_exception_info_to_admin_emails
    async def _process_reminders(self) -> None:
        await self.wait_until_ready()
        reminder_proc = ReminderProcessing()
        while not self.is_closed():
            await reminder_proc.iteration(const.BotBackend.DISCORD)
            await asyncio.sleep(const.REMINDER_POLLING_INTERVAL)

    @Mail.send_exception_info_to_admin_emails
    async def on_ready(self) -> None:
        bc.be.set_running(
            const.BotBackend.DISCORD, True,
            f"{self.user.name} {self.user.id} ({self.__class__.__name__}), instance: {self.instance_name}")
        bc.discord.bot_user_id = self.user.id
        self.bot_cache.update({
            "ready": True,
        })
        self.bot_cache.dump_to_file()
        bc.discord.guilds = self.guilds
        for guild in self.guilds:
            if guild.id not in self.config.discord.guilds.keys():
                self.config.discord.guilds[guild.id] = GuildSettings(guild.id)
        bc.discord.bot_user = self.user
        self.loop.create_task(self._config_autosave())

    @Mail.send_exception_info_to_admin_emails
    async def on_message(self, message: discord.Message) -> None:
        log.info(f"<{message.id}> {message.author} -> {message.content}")
        if isinstance(message.channel, discord.DMChannel):
            return
        if self.config.discord.guilds[message.channel.guild.id].ignored:
            return
        bc.message_cache.push(message.channel.id, CachedMsg(message.content, message.author.id))
        if message.author.id == self.user.id:
            return
        if message.channel.guild.id is None:
            return
        if self.config.discord.guilds[message.channel.guild.id].is_whitelisted:
            if message.channel.id not in self.config.discord.guilds[message.channel.guild.id].whitelist:
                return
        if message.author.id not in self.config.discord.users.keys():
            self.config.discord.users[message.author.id] = User(message.author.id)
        if self.config.discord.users[message.author.id].permission_level < 0:
            return
        if message.content.startswith(self.config.commands_prefix):
            await self._process_command(message)
        else:
            await self._process_regular_message(message)
            await MessageProcessing.process_repetitions(DiscordExecutionContext(message))
        execution_ctx = DiscordExecutionContext(message)
        await bc.plugin_manager.broadcast_command_interactive(execution_ctx, "on_message", execution_ctx)

    @Mail.send_exception_info_to_admin_emails
    async def on_message_edit(self, old_message: discord.Message, message: discord.Message) -> None:
        if message.content == old_message.content and message.embeds != old_message.embeds:
            log.info(f"<{message.id}> (edit, embed update) {message.author} -> {message.content}")
            return
        log.info(f"<{message.id}> (edit) {message.author} -> {message.content}")
        if isinstance(message.channel, discord.DMChannel):
            return
        if self.config.discord.guilds[message.channel.guild.id].ignored:
            return
        bc.message_cache.push(message.channel.id, CachedMsg(message.content, str(message.author.id)))
        if message.author.id == self.user.id:
            return
        if message.channel.guild.id is None:
            return
        if self.config.discord.guilds[message.channel.guild.id].is_whitelisted:
            if message.channel.id not in self.config.discord.guilds[message.channel.guild.id].whitelist:
                return
        if message.author.id not in self.config.discord.users.keys():
            self.config.discord.users[message.author.id] = User(message.author.id)
        if self.config.discord.users[message.author.id].permission_level < 0:
            return
        if (Time().now().astimezone() - message.created_at >
                datetime.timedelta(seconds=const.MAX_MESSAGE_TIMEDELTA_FOR_RECALCULATION)):
            return
        if message.content.startswith(self.config.commands_prefix):
            await self._process_command(message)

    async def _process_regular_message(self, message: discord.Message) -> None:
        channel_id = message.channel.id
        if isinstance(message.channel, discord.Thread):  # Inherit parent channel settings for threads
            channel_id = message.channel.parent_id
        if (self.user.mentioned_in(message) or self.user.id in [
                member.id for member in list(
                    itertools.chain(*[role.members for role in message.role_mentions]))]):
            # If the message is mentioning the bot or mentioning a role that the bot is in then
            # answer with result of processing command from config.on_mention_command
            if channel_id in self.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist:
                msg_content = message.content
                cmd = bc.config.commands_prefix + bc.config.on_mention_command
                cmd_split = cmd.split(" ")
                message.content = cmd
                result = await self._process_command(message, cmd_split, silent=True)
                message.content = msg_content
                result = result or ""
                if not self.config.discord.guilds[message.channel.guild.id].markov_pings:
                    result = await DiscordExecutionContext(message).disable_pings(result)
                await message.channel.send(message.author.mention + ' ' + result)
        elif channel_id in self.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist:
            # If the message is in a channel that is supposed to log markov chains, doesn't mention the bot then
            # add the message to the markov chain DB
            needs_to_be_added = True
            if not FF.is_enabled("WALBOT_FEATURE_MARKOV_MONGO"):
                for ignored_prefix in bc.markov.ignored_prefixes.values():
                    if message.content.startswith(ignored_prefix):
                        needs_to_be_added = False
                        break
            if needs_to_be_added:
                bc.markov.add_string(message.content)
        if channel_id in self.config.discord.guilds[message.channel.guild.id].responses_whitelist:
            # If the message is in a channel that is supposed to respond to messages then
            # answer with corresponding response from config.responses dictionary
            await MessageProcessing.process_responses(DiscordExecutionContext(message), message.content)
        if channel_id in self.config.discord.guilds[message.channel.guild.id].reactions_whitelist:
            # If the message is in a channel that is supposed to react to messages then
            # react to the message with corresponding reaction from config.reactions dictionary
            for reaction in self.config.reactions.values():
                if re.search(reaction.regex, message.content):
                    log.info("Added reaction " + reaction.emoji)
                    try:
                        await message.add_reaction(reaction.emoji)
                    except discord.HTTPException:
                        pass

    async def _process_command(self, message: discord.Message, command=None, silent=False) -> Optional[str]:
        if command is None:
            command = message.content.split(' ')
        command = list(filter(None, command))
        command[0] = command[0][1:]
        if not command[0]:
            return log.debug("Ignoring empty command")
        if command[0] not in self.config.commands.data.keys():
            if command[0] in self.config.commands.aliases.keys():
                command[0] = self.config.commands.aliases[command[0]]
            else:
                await message.channel.send(
                    f"Unknown command '{command[0]}', "
                    f"probably you meant '{self._suggest_similar_command(command[0])}'")
                return None
        max_exec_time = self.config.commands.data[command[0]].max_execution_time
        if command[0] in self.config.executor["commands_data"].keys():
            max_exec_time = bc.executor.commands[command[0]].max_execution_time
        if max_exec_time != -1:
            timeout_error, result = await Util.run_function_with_time_limit(
                self.config.commands.data[command[0]].run(
                    message, command, self.config.discord.users[message.author.id], silent=silent),
                max_exec_time)
            if command[0] not in (
                "silent",
            ) and timeout_error:
                await message.channel.send(f"Command '{' '.join(command)}' took too long to execute")
            return result
        else:
            return await self.config.commands.data[command[0]].run(
                message, command, self.config.discord.users[message.author.id], silent=silent)

    def _suggest_similar_command(self, unknown_command: str) -> str:
        min_dist = 100000
        suggestion = ""
        for command in self.config.commands.data.keys():
            dist = levenshtein_distance(unknown_command, command)
            if dist < min_dist:
                suggestion = command
                min_dist = dist
        for command in self.config.commands.aliases.keys():
            dist = levenshtein_distance(unknown_command, command)
            if dist < min_dist:
                suggestion = command
                min_dist = dist
        return suggestion

    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent) -> None:
        data = cast(Mapping[str, Any], payload.data)
        author = cast(Mapping[str, Any], data.get("author", {}))
        username = author.get("username", "")
        discriminator = author.get("discriminator", "")
        content = data.get("content", "")
        log.info(
            f"<{payload.message_id}> (raw_edit) {username}#{discriminator} -> {content}"
        )

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        log.info(f"<{payload.message_id}> (delete)")


class DiscordBotInstance(BotInstance):
    @Mail.send_exception_info_to_admin_emails
    def start(self, args, main_bot=True):
        log.info("Starting Discord instance...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Constructing bot instance
        intents = discord.Intents.all()
        if main_bot:
            walbot = WalBot(args.name, bc.config, bc.secret_config, intents=intents, fast_start=args.fast_start)
        else:
            walbot = importlib.import_module("src.backend.discord.minibot").MiniWalBot(
                args.name, bc.config, bc.secret_config, args.message, intents=intents)
        # Starting the bot
        try:
            walbot.run(bc.secret_config.discord["token"])
        except discord.PrivilegedIntentsRequired:
            log.error("Privileged Gateway Intents are not enabled! Shutting down the bot...")

    def stop(self, args, main_bot=True):
        pass

    def has_credentials(self):
        return bc.secret_config.discord["token"] is not None
