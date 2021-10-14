import asyncio
import datetime
import importlib
import itertools
import os
import random
import re
import signal
import shutil
import subprocess
import sys
import time
import zipfile

import discord
import psutil

from src import const
from src.algorithms import levenshtein_distance
from src.bc import DoNotUpdateFlag
from src.bot_cache import BotCache
from src.config import Command, Config, GuildSettings, SecretConfig, User, bc
from src.embed import DiscordEmbed
from src.emoji import get_clock_emoji
from src.ff import FF
from src.info import BotInfo
from src.log import log
from src.mail import Mail
from src.markov import Markov
from src.message import Msg
from src.reminder import Reminder
from src.repl import Repl
from src.utils import Util
from src.voice import VoiceRoutine


class WalBot(discord.Client):
    def __init__(self, name: str, config: Config, secret_config: SecretConfig, intents: discord.Intents) -> None:
        super().__init__(intents=intents)
        self.repl = None
        self.instance_name = name
        self.config = config
        self.secret_config = secret_config
        self.bot_cache = BotCache(True)
        self.loop.create_task(self._process_reminders())
        self.loop.create_task(VoiceRoutine(self.bot_cache).start())
        self.loop.create_task(self._repl_routine())
        bc.config = self.config
        bc.commands = self.config.commands
        bc.background_loop = self.loop
        bc.latency = lambda: self.latency
        bc.change_status = self._change_status
        bc.change_presence = self.change_presence
        bc.close = self.close
        bc.secret_config = self.secret_config
        bc.info = BotInfo()
        bc.plugin_manager.register()
        bc.fetch_channel = self.fetch_channel
        if not bc.args.fast_start:
            log.debug("Started Markov model checks...")
            if bc.markov.check():
                log.info("Markov model has passed all checks")
            else:
                log.info("Markov model has not passed checks, but all errors were fixed")

    async def _bot_runner_task(self, *args, **kwargs):
        try:
            await self.start(*args, **kwargs)
        finally:
            if not self.is_closed():
                await self.close()

    def run(self, *args, **kwargs):
        # Sightly patched implementation from discord.py discord.Client (parent) class
        # Reference: https://github.com/Rapptz/discord.py/blob/master/discord/client.py
        loop = self.loop
        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass
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
        for event in bc.background_events:
            event.cancel()
        bc.background_loop = None
        await bc.plugin_manager.broadcast_command("close")

    @Mail.send_exception_info_to_admin_emails_async
    async def _precompile(self) -> None:
        log.debug("Started precompiling functions...")
        levenshtein_distance("", "")
        log.debug("Finished precompiling functions")

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

    async def _process_reminders_iteration(self) -> None:
        log.debug3("Reminder processing iteration has started")
        now = datetime.datetime.now().replace(second=0).strftime(const.REMINDER_DATETIME_FORMAT)
        to_remove = []
        to_append = []
        reminder_do_not_update_flag = False
        for key, rem in self.config.reminders.items():
            for i in range(len(rem.prereminders_list)):
                prereminder = rem.prereminders_list[i]
                used_prereminder = rem.used_prereminders_list[i]
                if prereminder == 0 or used_prereminder:
                    continue
                prereminder_time = (
                    datetime.datetime.now().replace(second=0) + datetime.timedelta(minutes=prereminder))
                if rem == prereminder_time.strftime(const.REMINDER_DATETIME_FORMAT):
                    channel = self.get_channel(rem.channel_id)
                    e = DiscordEmbed()
                    clock_emoji = get_clock_emoji(datetime.datetime.now().strftime("%H:%M"))
                    e.title(f"{prereminder} minutes left until reminder")
                    e.description(rem.message + "\n" + rem.notes)
                    e.color(random.randint(0x000000, 0xffffff))
                    e.timestamp(
                        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=prereminder))
                    e.footer(text=rem.author)
                    await channel.send("", embed=e.get())
                    rem.used_prereminders_list[i] = True
            if rem == now:
                channel = self.get_channel(rem.channel_id)
                clock_emoji = get_clock_emoji(datetime.datetime.now().strftime("%H:%M"))
                e = DiscordEmbed()
                e.title(f"{clock_emoji} You asked to remind")
                e.description(rem.message + "\n" + rem.notes)
                e.color(random.randint(0x000000, 0xffffff))
                e.timestamp(datetime.datetime.now(datetime.timezone.utc))
                e.footer(text=rem.author)
                await channel.send(' '.join(rem.ping_users if rem.ping_users else ""), embed=e.get())
                for user_id in rem.whisper_users:
                    await Msg.send_direct_message(
                        self.get_user(user_id), f"You asked to remind at {now} -> {rem.message}", False)
                if rem.email_users:
                    mail = Mail(self.secret_config)
                    mail.send(
                        rem.email_users,
                        f"Reminder: {rem.message}",
                        f"You asked to remind at {now} -> {rem.message}")
                if rem.repeat_after > 0:
                    new_time = datetime.datetime.now().replace(second=0, microsecond=0) + rem.get_next_event_delta()
                    new_time = new_time.strftime(const.REMINDER_DATETIME_FORMAT)
                    to_append.append(
                        Reminder(str(new_time), rem.message, rem.channel_id, rem.author, rem.time_created))
                    to_append[-1].repeat_after = rem.repeat_after
                    to_append[-1].repeat_interval_measure = rem.repeat_interval_measure
                    to_append[-1].prereminders_list = rem.prereminders_list
                    to_append[-1].used_prereminders_list = [False] * len(rem.prereminders_list)
                    to_append[-1].notes = rem.notes
                    log.debug2(f"Scheduled renew of recurring reminder - old id: {key}")
                to_remove.append(key)
            elif rem < now:
                log.debug2(f"Scheduled reminder with id {key} removal")
                to_remove.append(key)
            else:
                prereminders_delay = 0
                if rem.prereminders_list:
                    prereminders_delay = max(rem.prereminders_list)
                if ((datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - datetime.datetime.now())
                        < datetime.timedelta(minutes=(5 + prereminders_delay / 60))):
                    reminder_do_not_update_flag = True
        bc.do_not_update[DoNotUpdateFlag.REMINDER] = reminder_do_not_update_flag
        for key in to_remove:
            self.config.reminders.pop(key)
        for item in to_append:
            key = self.config.ids["reminder"]
            self.config.reminders[key] = item
            self.config.ids["reminder"] += 1
        log.debug3("Reminder processing iteration has finished")

    @Mail.send_exception_info_to_admin_emails_async
    async def _process_reminders(self) -> None:
        await self.wait_until_ready()
        while not self.is_closed():
            await self._process_reminders_iteration()
            await asyncio.sleep(const.REMINDER_POLLING_INTERVAL)

    async def _repl_routine(self) -> None:
        self.repl = Repl(self.config.repl["port"])
        await self.repl.start()

    @Mail.send_exception_info_to_admin_emails_async
    async def on_ready(self) -> None:
        self._load_plugins()
        log.info(
            f"Logged in as: {self.user.name} {self.user.id} ({self.__class__.__name__}), "
            f"instance: {self.instance_name}")
        self.bot_cache.update({
            "ready": True,
        })
        self.bot_cache.dump_to_file()
        bc.guilds = self.guilds
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)
        bc.bot_user = self.user
        self.loop.create_task(self._config_autosave())
        self.loop.create_task(self._precompile())

    def _load_plugins(self) -> None:
        for plugin_name in bc.plugin_manager.get_plugins_list():
            if plugin_name not in self.config.plugins.keys():
                self.config.plugins[plugin_name] = {
                    "autostart": False,
                }
        for plugin_name, plugin_state in self.config.plugins.items():
            if plugin_state["autostart"]:
                asyncio.create_task(bc.plugin_manager.send_command(plugin_name, "init"))

    @Mail.send_exception_info_to_admin_emails_async
    async def on_message(self, message: discord.Message) -> None:
        await bc.plugin_manager.broadcast_command("on_message", message)
        if self.config.guilds[message.channel.guild.id].ignored:
            return
        bc.message_buffer.push(message)
        log.info(f"<{message.id}> {message.author} -> {message.content}")
        if message.author.id == self.user.id:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.guild.id is None:
            return
        if self.config.guilds[message.channel.guild.id].is_whitelisted:
            if message.channel.id not in self.config.guilds[message.channel.guild.id].whitelist:
                return
        if message.author.id not in self.config.users.keys():
            self.config.users[message.author.id] = User(message.author.id)
        if self.config.users[message.author.id].permission_level < 0:
            return
        if message.content.startswith(self.config.commands_prefix):
            await self._process_command(message)
        else:
            await self._process_regular_message(message)
            await self._process_repetitions(message)

    @Mail.send_exception_info_to_admin_emails_async
    async def on_message_edit(self, old_message: discord.Message, message: discord.Message) -> None:
        if message.embeds != old_message.embeds:
            log.info(f"<{message.id}> (edit, embed update) {message.author} -> {message.content}")
            return
        if self.config.guilds[message.channel.guild.id].ignored:
            return
        bc.message_buffer.push(message)
        log.info(f"<{message.id}> (edit) {message.author} -> {message.content}")
        if message.author.id == self.user.id:
            return
        if isinstance(message.channel, discord.DMChannel):
            return
        if message.channel.guild.id is None:
            return
        if self.config.guilds[message.channel.guild.id].is_whitelisted:
            if message.channel.id not in self.config.guilds[message.channel.guild.id].whitelist:
                return
        if message.author.id not in self.config.users.keys():
            self.config.users[message.author.id] = User(message.author.id)
        if self.config.users[message.author.id].permission_level < 0:
            return
        if message.content.startswith(self.config.commands_prefix):
            await self._process_command(message)

    async def _process_repetitions(self, message: discord.Message) -> None:
        m = tuple(bc.message_buffer.get(message.channel.id, i) for i in range(3))
        if (all(m) and m[0].content and m[0].content == m[1].content == m[2].content and
            (m[0].author.id != self.user.id and
             m[1].author.id != self.user.id and
             m[2].author.id != self.user.id)):
            await message.channel.send(m[0].content)

    async def _process_regular_message(self, message: discord.Message) -> None:
        if (self.user.mentioned_in(message) or self.user.id in [
                member.id for member in list(
                    itertools.chain(*[role.members for role in message.role_mentions]))]):
            if message.channel.id in self.config.guilds[message.channel.guild.id].markov_responses_whitelist:
                result = await self.config.disable_pings_in_response(message, bc.markov.generate())
                await message.channel.send(message.author.mention + ' ' + result)
        elif message.channel.id in self.config.guilds[message.channel.guild.id].markov_logging_whitelist:
            bc.markov.add_string(message.content)
        if message.channel.id in self.config.guilds[message.channel.guild.id].responses_whitelist:
            responses_count = 0
            for response in self.config.responses.values():
                if responses_count >= const.MAX_BOT_RESPONSES_ON_ONE_MESSAGE:
                    break
                if re.search(response.regex, message.content):
                    text = await Command.process_subcommands(
                        response.text, message, self.config.users[message.author.id])
                    await Msg.reply(message, text, False)
                    responses_count += 1
        if message.channel.id in self.config.guilds[message.channel.guild.id].reactions_whitelist:
            for reaction in self.config.reactions.values():
                if re.search(reaction.regex, message.content):
                    log.info("Added reaction " + reaction.emoji)
                    try:
                        await message.add_reaction(reaction.emoji)
                    except discord.HTTPException:
                        pass

    async def _process_command(self, message: discord.Message) -> None:
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
                return
        await self.config.commands.data[command[0]].run(message, command, self.config.users[message.author.id])

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
        try:
            log.info(f"<{payload.message_id}> (raw_edit) {payload.data['author']['username']}#"
                     f"{payload.data['author']['discriminator']} -> {payload.data['content']}")
        except KeyError:
            pass

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent) -> None:
        log.info(f"<{payload.message_id}> (delete)")


def start(args, main_bot=True):
    # Check whether bot is already running
    bot_cache = BotCache(main_bot).parse()
    if bot_cache is not None:
        pid = bot_cache["pid"]
        if pid is not None and psutil.pid_exists(pid):
            return log.error("Bot is already running!")
    # Some variable initializations
    config = None
    secret_config = None
    bc.restart_flag = False
    bc.args = args
    # Handle --nohup flag
    if sys.platform in ("linux", "darwin") and args.nohup:
        fd = os.open(const.NOHUP_FILE_PATH, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        log.info(f"Output is redirected to {const.NOHUP_FILE_PATH}")
        os.dup2(fd, sys.stdout.fileno())
        os.dup2(sys.stdout.fileno(), sys.stderr.fileno())
        os.close(fd)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
    # Selecting YAML parser
    bc.yaml_loader, bc.yaml_dumper = Util.get_yaml(verbose=True)
    # Saving application pd in order to safely stop it later
    BotCache(main_bot).dump_to_file()
    # Executing patch tool if it is necessary
    if args.patch:
        cmd = f"'{sys.executable}' '{os.path.dirname(__file__) + '/../tools/patch.py'}' all"
        log.info("Executing patch tool: " + cmd)
        subprocess.call(cmd)
    # Read configuration files
    config = Util.read_config_file(const.CONFIG_PATH)
    if config is None:
        config = Config()
    secret_config = Util.read_config_file(const.SECRET_CONFIG_PATH)
    if secret_config is None:
        secret_config = SecretConfig()
    bc.markov = Util.read_config_file(const.MARKOV_PATH)
    if bc.markov is None and os.path.isdir("backup"):
        # Check available backups
        markov_backups = sorted([x for x in os.listdir("backup") if x.startswith("markov_") and x.endswith(".zip")])
        if markov_backups:
            # Restore Markov model from backup
            with zipfile.ZipFile("backup/" + markov_backups[-1], 'r') as zip_ref:
                zip_ref.extractall(".")
            log.info(f"Restoring Markov model from backup/{markov_backups[-1]}")
            shutil.move(markov_backups[-1][:-4], "markov.yaml")
            bc.markov = Util.read_config_file(const.MARKOV_PATH)
            if bc.markov is None:
                bc.markov = Markov()
                log.warning("Failed to restore Markov model from backup. Creating new Markov model...")
    if bc.markov is None:
        bc.markov = Markov()
        log.info("Created empty Markov model")
    # Check config versions
    ok = True
    ok &= Util.check_version(
        "discord.py", discord.__version__, const.DISCORD_LIB_VERSION,
        solutions=[
            "execute: python -m pip install -r requirements.txt",
        ])
    ok &= Util.check_version(
        "Config", config.version, const.CONFIG_VERSION,
        solutions=[
            "run patch tool",
            "remove config.yaml (settings will be lost!)",
        ])
    ok &= Util.check_version(
        "Markov config", bc.markov.version, const.MARKOV_CONFIG_VERSION,
        solutions=[
            "run patch tool",
            "remove markov.yaml (Markov model will be lost!)",
        ])
    ok &= Util.check_version(
        "Secret config", secret_config.version, const.SECRET_CONFIG_VERSION,
        solutions=[
            "run patch tool",
            "remove secret.yaml (your Discord authentication token will be lost!)",
        ])
    if main_bot and not ok:
        sys.exit(const.ExitStatus.CONFIG_FILE_ERROR)
    config.commands.update()
    # Checking authentication token
    if secret_config.token is None:
        secret_config = SecretConfig()
        if not FF.is_enabled("WALBOT_FEATURE_NEW_CONFIG"):
            secret_config.token = input("Enter your token: ")
    # Constructing bot instance
    if main_bot:
        intents = discord.Intents.all()
        walbot = WalBot(args.name, config, secret_config, intents=intents)
    else:
        walbot = importlib.import_module("src.minibot").MiniWalBot(args.name, config, secret_config, args.message)
    # Starting the bot
    try:
        walbot.run(secret_config.token)
    except discord.errors.PrivilegedIntentsRequired:
        log.error("Privileged Gateway Intents are not enabled! Shutting down the bot...")
    # After stopping the bot
    log.info("Bot is disconnected!")
    if main_bot:
        config.save(const.CONFIG_PATH, const.MARKOV_PATH, const.SECRET_CONFIG_PATH, wait=True)
    BotCache(main_bot).remove()
    if bc.restart_flag:
        cmd = f"'{sys.executable}' '{os.path.dirname(os.path.dirname(__file__)) + '/walbot.py'}' start"
        log.info("Calling: " + cmd)
        if sys.platform in ("linux", "darwin"):
            fork = os.fork()
            if fork == 0:
                subprocess.call(cmd)
            elif fork > 0:
                log.info("Stopping current instance of the bot")
                sys.exit(const.ExitStatus.NO_ERROR)
        else:
            subprocess.call(cmd)


def stop(_, main_bot=True):
    if not BotCache(main_bot).exists():
        return log.error("Could not stop the bot (cache file does not exist)")
    bot_cache = BotCache(main_bot).parse()
    pid = bot_cache["pid"]
    if pid is None:
        return log.error("Could not stop the bot (cache file does not contain pid)")
    if psutil.pid_exists(pid):
        if sys.platform == "win32":
            # Reference to the original solution:
            # https://stackoverflow.com/a/64357453
            import ctypes

            kernel = ctypes.windll.kernel32
            kernel.FreeConsole()
            kernel.AttachConsole(pid)
            kernel.SetConsoleCtrlHandler(None, 1)
            kernel.GenerateConsoleCtrlEvent(0, 0)
        else:
            os.kill(pid, signal.SIGINT)
        while psutil.pid_exists(pid):
            log.debug("Bot is still running. Please, wait...")
            time.sleep(0.5)
        log.info("Bot is stopped!")
    else:
        log.error("Could not stop the bot (bot is not running)")
        BotCache(main_bot).remove()
