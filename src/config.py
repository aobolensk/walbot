import asyncio
import datetime
import importlib
import inspect
import os
import sys
import threading
import uuid
import zipfile

import discord
import yaml

from src import const
from src.backend.discord.message import Msg
from src.bc import BotController, DoNotUpdateFlag
from src.log import log
from src.utils import Util, null

bc = BotController()


class Command:
    def __init__(self, module_name=None, class_name=None,
                 perform=None, message=None, cmd_line=None, permission=0, subcommand=False,
                 max_execution_time=None):
        self.module_name = module_name
        self.class_name = class_name
        self.perform = perform
        self.permission = permission
        self.subcommand = subcommand
        self.message = message
        self.cmd_line = cmd_line
        self.is_global = False
        self.channels = []
        self.times_called = 0
        self.max_execution_time = max_execution_time or const.MAX_COMMAND_EXECUTION_TIME

    def is_available(self, channel_id):
        return self.is_global or (channel_id in self.channels)

    def can_be_subcommand(self):
        return self.subcommand or self.message or self.cmd_line

    def get_actor(self):
        return getattr(getattr(sys.modules[self.module_name], self.class_name), self.perform)

    @staticmethod
    async def process_subcommands(content, message, user, safe=False):
        command_indicators = {
            ')': '(',
            ']': '[',
            '`': '`',
            '}': '{',
        }
        while True:
            updated = False
            for i in range(len(content)):
                if content[i] in command_indicators.keys():
                    for j in range(i - 1, 0, -1):
                        if content[j] == command_indicators[content[i]] and content[j - 1] == '$':
                            updated = True
                            message.content = content[j + 1:i]
                            command = message.content.split()
                            if not command:
                                return
                            if command[0] not in bc.config.commands.data.keys():
                                if command[0] in bc.config.commands.aliases.keys():
                                    command[0] = bc.config.commands.aliases[command[0]]
                                else:
                                    await message.channel.send(f"Unknown command '{command[0]}'")
                            result = ""
                            if command and command[0] in bc.commands.data.keys():
                                log.debug(f"Processing subcommand: {command[0]}: {message.content}")
                                cmd = bc.commands.data[command[0]]
                                if cmd.can_be_subcommand():
                                    result = await cmd.run(message, command, user, silent=True)
                                    if result is None or (safe and not const.ALNUM_STRING_REGEX.match(content)):
                                        result = ""
                                else:
                                    await message.channel.send(f"Command '{command[0]}' can not be used as subcommand")
                            content = content[:j - 1] + result + content[i + 1:]
                            log.debug2(f"Command (during processing subcommands): {content}")
                            break
                if updated:
                    break
            if not updated:
                break
        return content

    async def run(self, message, command, user, silent=False):
        if len(inspect.stack(0)) >= const.MAX_SUBCOMMAND_DEPTH:
            return null(await message.channel.send("ERROR: Maximum subcommand depth is reached!"))
        log.debug(f"Processing command: {message.content}")
        channel_id = message.channel.id
        if isinstance(message.channel, discord.Thread):  # Inherit command permissions for threads
            channel_id = message.channel.parent_id
        if not self.is_available(channel_id):
            return null(await message.channel.send(f"Command '{command[0]}' is not available in this channel"))
        if user is not None and self.permission > user.permission_level:
            return null(await message.channel.send(f"You don't have permission to call command '{command[0]}'"))
        self.times_called += 1
        postpone_execution = [
            "addcmd",
            "updcmd",
            "addextcmd",
            "updextcmd",
            "addbgevent",
            "addresponse",
            "updresponse",
        ]
        from src.api.command import Command as ApiCommand
        from src.backend.discord.context import DiscordExecutionContext
        if message.content.split(' ')[0][1:] not in postpone_execution:
            log.debug2(f"Command (before processing): {message.content}")
            message.content = ApiCommand.process_variables(DiscordExecutionContext(message), message.content, command)
            log.debug2(f"Command (after processing variables): {message.content}")
            message.content = await self.process_subcommands(message.content, message, user)
            log.debug2(f"Command (after processing subcommands): {message.content}")
        else:
            log.debug2("Subcommands are not processed!")
        command = message.content[1:].split(' ')
        command = list(filter(None, command))
        if self.perform is not None:
            return await self.get_actor()(message, command, silent)
        elif self.message is not None:
            response = self.message
            log.debug2(f"Command (before processing): {response}")
            response = ApiCommand.process_variables(DiscordExecutionContext(message), response, command)
            log.debug2(f"Command (after processing variables): {response}")
            response = await self.process_subcommands(response, message, user)
            log.debug2(f"Command (after processing subcommands): {response}")
            if response:
                if not silent:
                    if len(response) > const.DISCORD_MAX_MESSAGE_LENGTH * 5:
                        await message.channel.send(
                            "ERROR: Max message length exceeded "
                            f"({len(response)} > {const.DISCORD_MAX_MESSAGE_LENGTH * 5})")
                    elif len(const.UNICODE_EMOJI_REGEX.findall(response)) > 50:
                        await message.channel.send(
                            "ERROR: Max amount of Unicode emojis for one message exceeded "
                            f"({len(const.UNICODE_EMOJI_REGEX.findall(response))} > {50})")
                    else:
                        for chunk in Msg.split_by_chunks(response, const.DISCORD_MAX_MESSAGE_LENGTH):
                            await message.channel.send(chunk)
                return response
        elif self.cmd_line is not None:
            cmd_line = self.cmd_line[:]
            log.debug2(f"Command (before processing): {cmd_line}")
            cmd_line = ApiCommand.process_variables(DiscordExecutionContext(message), cmd_line)
            log.debug2(f"Command (after processing variables): {cmd_line}")
            cmd_line = await self.process_subcommands(cmd_line, message, user, safe=True)
            log.debug2(f"Command (after processing subcommands): {cmd_line}")
            return await Util.run_external_command(message, cmd_line, silent)
        else:
            await message.channel.send(f"Command '{command[0]}' is not callable")


class BackgroundEvent:
    def __init__(self, config, channel, message, period):
        self.config = config
        self.channel = channel
        self.message = message
        self.period = period
        self.task = bc.background_loop.create_task(self.run())

    async def run(self):
        command = self.message.content.split(' ')
        command = list(filter(None, command))
        command[0] = command[0][1:]
        while True:
            await asyncio.sleep(self.period)
            log.debug(f"Triggered background event: {' '.join(command)}")
            if command[0] not in self.config.commands.data.keys():
                await self.channel.send(f"Unknown command '{command[0]}'")
            else:
                cmd = self.config.commands.data[command[0]]
                saved_content = self.message.content
                await cmd.run(self.message, command, None)
                self.message.content = saved_content

    def cancel(self):
        self.task.cancel()


class Reaction:
    def __init__(self, regex, emoji):
        self.regex = regex
        self.emoji = emoji


class Response:
    def __init__(self, regex, text):
        self.regex = regex
        self.text = text


class GuildSettings:
    def __init__(self, id_):
        self.id = id_
        self.is_whitelisted = False
        self.whitelist = set()
        self.markov_logging_whitelist = set()
        self.markov_responses_whitelist = set()
        self.responses_whitelist = set()
        self.reactions_whitelist = set()
        self.markov_pings = True
        self.ignored = False


class User:
    def __init__(self, id_):
        self.id = id_
        self.permission_level = const.Permission.USER.value


class Config:
    def __init__(self):
        commands = importlib.import_module("src.commands")
        self.commands = commands.Commands()
        self.commands.update()
        self.version = const.CONFIG_VERSION
        self.reactions = dict()
        self.guilds = dict()
        self.users = dict()
        self.reminders = dict()
        self.responses = dict()
        self.quotes = dict()
        self.plugins = dict()
        self.commands_prefix = "!"
        self.on_mention_command = "markov"
        self.ids = {
            "reminder": 1,
            "reaction": 1,
            "response": 1,
            "quote": 1,
            "timer": 1,
            "stopwatch": 1,
            "markov_ignored_prefix": 1,
        }
        self.saving = {
            "backup": {
                "compress": True,
                "period": 10,
            },
            "period": 10,
        }
        self.repl = {
            "port": 8080,
        }
        self.telegram = {
            "channel_whitelist": set(),
            "passphrase": uuid.uuid4().hex,
        }

    def backup(self, *files):
        compress_type = zipfile.ZIP_DEFLATED if self.saving["backup"]["compress"] else zipfile.ZIP_STORED
        for file in files:
            path = os.path.dirname(file)
            name, ext = os.path.splitext(os.path.basename(file))
            name += "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = name + ext
            backup_archive = os.path.join(path, "backup", name + ext + ".zip")
            if not os.path.exists("backup"):
                os.makedirs("backup")
            try:
                with zipfile.ZipFile(backup_archive, mode='w') as zf:
                    zf.write(file, arcname=backup_file, compress_type=compress_type)
            except Exception as e:
                log.error(f"Unable to create backup {file} -> {backup_file}: {e}")
            else:
                log.info(f"Created backup for {file}: {backup_file}")

    def save(self, config_file, markov_file, secret_config_file, wait=False):
        config_mutex = threading.Lock()
        with config_mutex:
            log.info("Saving of config is started")
            with open(config_file, 'wb') as f:
                try:
                    f.write(yaml.dump(
                        self,
                        Dumper=bc.yaml_dumper,
                        encoding='utf-8',
                        allow_unicode=True))
                    log.info("Saving of config is finished")
                except Exception:
                    log.error("yaml.dump failed", exc_info=True)
        secret_config_mutex = threading.Lock()
        with secret_config_mutex:
            log.info("Saving of secret config is started")
            with open(secret_config_file, 'wb') as f:
                try:
                    f.write(yaml.dump(
                        bc.secret_config,
                        Dumper=bc.yaml_dumper,
                        encoding='utf-8',
                        allow_unicode=True))
                    log.info("Saving of secret config is finished")
                except Exception:
                    log.error("yaml.dump failed", exc_info=True)
        if bc.do_not_update[DoNotUpdateFlag.VOICE]:
            # If bot is connected to voice channel, don't save markov data because it causes sound lags
            return log.info("Markov module save is skipped since bot is in voice channel")
        markov_mutex = threading.Lock()
        with markov_mutex:
            log.info("Saving of Markov module data is started")
            try:
                thread = threading.Thread(
                    target=bc.markov.serialize,
                    args=(markov_file, bc.yaml_dumper))
                thread.start()
                if wait:
                    log.info("Waiting for saving of Markov module data...")
                    thread.join()
                    log.info("Saving of Markov module data is finished")
            except Exception:
                log.error("Saving of Markov module data is failed", exc_info=True)


class SecretConfig:
    def __init__(self):
        self.version = const.SECRET_CONFIG_VERSION
        self.mail = {
            "smtp_server": None,
            "email": None,
            "password": None,
        }
        self.telegram = {
            "token": None,
        }
        self.discord = {
            "token": None,
        }
        self.admin_email_list = list()
