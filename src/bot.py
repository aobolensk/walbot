import asyncio
import datetime
import importlib
import itertools
import os
import re
import signal
import sys
import time

import discord
import psutil

from src import const
from src.algorithms import levenshtein_distance
from src.bot_cache import BotCache
from src.config import Command, Config, DoNotUpdateFlag, GuildSettings, SecretConfig, User, bc
from src.embed import DiscordEmbed
from src.info import BotInfo
from src.log import log
from src.markov import Markov
from src.message import Msg
from src.message_buffer import MessageBuffer
from src.reminder import Reminder
from src.repl import Repl
from src.utils import Util


class WalBot(discord.Client):
    def __init__(self, config, secret_config):
        super().__init__()
        self.repl = None
        self.config = config
        self.secret_config = secret_config
        self.loop.create_task(self.config_autosave())
        self.loop.create_task(self.process_reminders())
        self.loop.create_task(self._precompile())
        self.loop.create_task(self.voice_routine())
        self.bot_cache = BotCache(True)
        bc.config = self.config
        bc.commands = self.config.commands
        bc.background_loop = self.loop
        bc.latency = lambda: self.latency
        bc.change_status = self.change_status
        bc.change_presence = self.change_presence
        bc.close = self.close
        bc.secret_config = self.secret_config
        bc.message_buffer = MessageBuffer()
        bc.info = BotInfo()
        if not bc.args.fast_start:
            log.debug("Started Markov model checks...")
            if bc.markov.check():
                log.info("Markov model has passed all checks")
            else:
                log.info("Markov model has not passed checks, but all errors were fixed")

    async def update_autoupdate_flag(self, current_autoupdate_flag):
        if current_autoupdate_flag != self.bot_cache.get_state()["do_not_update"]:
            self.bot_cache.update({"do_not_update": current_autoupdate_flag})
            self.bot_cache.dump_to_file()

    async def voice_routine(self):
        # Disconnect if bot is inactive in voice channel
        voice_client_queue_disconnect_counter = 0

        while True:
            if bc.voice_client:
                bc.do_not_update[DoNotUpdateFlag.VOICE] = True
            else:
                bc.do_not_update[DoNotUpdateFlag.VOICE] = False
            await self.update_autoupdate_flag(any(bc.do_not_update))
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
                else:
                    pass
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

    async def _precompile(self):
        log.debug("Started precompiling functions...")
        levenshtein_distance("", "")
        log.debug("Finished precompiling functions")

    async def change_status(self, string, type_):
        await self.change_presence(activity=discord.Activity(name=string, type=type_))

    async def config_autosave(self):
        await self.wait_until_ready()
        index = 1
        while not self.is_closed():
            if index % self.config.saving["backup"]["period"] == 0:
                self.config.backup(const.CONFIG_PATH, const.MARKOV_PATH)
            self.config.save(const.CONFIG_PATH, const.MARKOV_PATH, const.SECRET_CONFIG_PATH)
            index += 1
            await asyncio.sleep(self.config.saving["period"] * 60)

    async def process_reminders(self):
        await self.wait_until_ready()
        while not self.is_closed():
            log.debug3("Reminder processing iteration has started")
            now = datetime.datetime.now().replace(second=0).strftime(const.REMINDER_DATETIME_FORMAT)
            to_remove = []
            to_append = []
            reminder_do_not_update_flag = False
            for key, rem in self.config.reminders.items():
                if rem == now:
                    channel = self.get_channel(rem.channel_id)
                    e = DiscordEmbed()
                    e.title("You asked to remind")
                    e.description(rem.message)
                    e.color(0xcc1818)
                    e.timestamp(datetime.datetime.now(datetime.timezone.utc))
                    e.footer(text=rem.author)
                    await channel.send(' '.join(rem.ping_users if rem.ping_users else ""), embed=e.get())
                    for user_id in rem.whisper_users:
                        await Msg.send_direct_message(
                            self.get_user(user_id), f"You asked to remind at {now} -> {rem.message}", False)
                    if rem.repeat_after > 0:
                        new_time = datetime.datetime.now().replace(second=0, microsecond=0) + rem.get_next_event_delta()
                        new_time = new_time.strftime(const.REMINDER_DATETIME_FORMAT)
                        to_append.append(
                            Reminder(str(new_time), rem.message, rem.channel_id, rem.author, rem.time_created))
                        to_append[-1].repeat_after = rem.repeat_after
                        to_append[-1].repeat_interval_measure = rem.repeat_interval_measure
                        log.debug2(f"Scheduled renew of recurring reminder - old id: {key}")
                    to_remove.append(key)
                elif rem < now:
                    log.debug2(f"Scheduled reminder with id {key} removal")
                    to_remove.append(key)
                else:
                    if ((datetime.datetime.strptime(rem.time, const.REMINDER_DATETIME_FORMAT) - datetime.datetime.now())
                            < datetime.timedelta(minutes=5)):
                        reminder_do_not_update_flag = True
            bc.do_not_update[DoNotUpdateFlag.REMINDER] = reminder_do_not_update_flag
            for key in to_remove:
                self.config.reminders.pop(key)
            for item in to_append:
                key = self.config.ids["reminder"]
                self.config.reminders[key] = item
                self.config.ids["reminder"] += 1
            log.debug3("Reminder processing iteration has finished")
            await asyncio.sleep(const.REMINDER_POLLING_INTERVAL)

    async def on_ready(self):
        log.info(f"Logged in as: {self.user.name} {self.user.id} ({self.__class__.__name__})")
        self.bot_cache.update({
            "ready": True,
        })
        self.bot_cache.dump_to_file()
        if sys.platform == "win32":
            log.warning("REPL is disabled on Windows for now")
        else:
            self.repl = Repl(self.config.repl["port"])
        bc.guilds = self.guilds
        for guild in self.guilds:
            if guild.id not in self.config.guilds.keys():
                self.config.guilds[guild.id] = GuildSettings(guild.id)
        bc.bot_user = self.user

    async def on_message(self, message):
        try:
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
                await self.process_command(message)
            else:
                await self.process_regular_message(message)
                await self.process_repetitions(message)
        except Exception:
            log.error("on_message failed", exc_info=True)

    async def process_repetitions(self, message):
        m = tuple(bc.message_buffer.get(message.channel.id, i) for i in range(3))
        if (all(m) and m[0].content == m[1].content == m[2].content and
            (m[0].author.id != self.user.id and
             m[1].author.id != self.user.id and
             m[2].author.id != self.user.id)):
            await message.channel.send(m[0].content)

    async def process_regular_message(self, message):
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

    async def process_command(self, message):
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
                    f"probably you meant '{self.suggest_similar_command(command[0])}'")
                return
        await self.config.commands.data[command[0]].run(message, command, self.config.users[message.author.id])

    def suggest_similar_command(self, unknown_command):
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

    async def on_raw_message_edit(self, payload):
        try:
            log.info(f"<{payload.message_id}> (edit) {payload.data['author']['username']}#"
                     f"{payload.data['author']['discriminator']} -> {payload.data['content']}")
        except KeyError:
            pass

    async def on_raw_message_delete(self, payload):
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
        os.system(cmd)
    # Read configuration files
    config = Util.read_config_file(const.CONFIG_PATH)
    if config is None:
        config = Config()
    secret_config = Util.read_config_file(const.SECRET_CONFIG_PATH)
    if secret_config is None:
        secret_config = SecretConfig()
    bc.markov = Util.read_config_file(const.MARKOV_PATH)
    if bc.markov is None:
        bc.markov = Markov()
    # Check config versions
    ok = True
    ok &= Util.check_version(
        "discord.py", discord.__version__, const.DISCORD_LIB_VERSION,
        solutions=[
            "execute: python -m pip install -r requirements.txt",
        ], fatal=False)
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
    if not ok:
        sys.exit(const.ExitStatus.CONFIG_FILE_ERROR)
    config.commands.update()
    # Constructing bot instance
    if main_bot:
        walbot = WalBot(config, secret_config)
    else:
        walbot = importlib.import_module("src.minibot").MiniWalBot(config, secret_config, args.message)
    # Checking authentication token
    if secret_config.token is None:
        secret_config.token = input("Enter your token: ")
    # Starting the bot
    walbot.run(secret_config.token)
    # After stopping the bot
    if walbot.repl is not None:
        walbot.repl.stop()
    for event in bc.background_events:
        event.cancel()
    bc.background_loop = None
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
                os.system(cmd)
            elif fork > 0:
                log.info("Stopping current instance of the bot")
                sys.exit(const.ExitStatus.NO_ERROR)
        else:
            os.system(cmd)


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
