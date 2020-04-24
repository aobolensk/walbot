import asyncio
import datetime
import os
import threading
import re
import yaml
import zipfile

from . import const
from .log import log
from .utils import Util


class BotController:
    def __init__(self):
        self.background_events = []
        self.background_loop = None
        self.deployment_time = datetime.datetime.now()


bc = BotController()


class Command:
    def __init__(self, name, perform=None, message=None, permission=0, subcommand=False):
        self.name = name
        self.perform = perform
        self.permission = permission
        self.subcommand = subcommand
        self.message = message
        self.is_global = False
        self.channels = []

    def is_available(self, channel_id):
        return self.is_global or (channel_id in self.channels)

    def can_be_subcommand(self):
        return self.subcommand or self.message

    async def process_subcommands(self, content, message, user):
        while True:
            updated = False
            for i in range(len(content)):
                if content[i] == ')':
                    for j in range(i-1, 0, -1):
                        if content[j] == '(' and content[j-1] == '$':
                            updated = True
                            message.content = content[j+1:i]
                            command = message.content.split()
                            if command[0] not in bc.config.commands.data.keys():
                                if command[0] in bc.config.commands.aliases.keys():
                                    command[0] = bc.config.commands.aliases[command[0]]
                                else:
                                    await message.channel.send("Unknown command '{}'".format(command[0]))
                            result = ""
                            if len(command) > 0 and command[0] in bc.commands.data.keys():
                                log.debug("Processing subcommand: {}: {}".format(command[0], message.content))
                                actor = bc.commands.data[command[0]]
                                if actor.can_be_subcommand():
                                    result = await actor.run(message, command, user, silent=True)
                                    if result is None:
                                        result = ""
                                else:
                                    await message.channel.send("Command '{}' can not be used as subcommand"
                                                               .format(command[0]))
                            content = content[:j-1] + result + content[i+1:]
                            break
                if updated:
                    break
            if not updated:
                break
        return content

    async def run(self, message, command, user, silent=False):
        log.debug("Processing command: {}".format(message.content))
        if not self.is_available(message.channel.id):
            await message.channel.send("Command '{}' is not available in this channel".format(command[0]))
            return
        if user is not None and self.permission > user.permission_level:
            await message.channel.send("You don't have permission to call command '{}'".format(command[0]))
            return
        if not hasattr(self, "times_called"):
            self.times_called = 1
        else:
            self.times_called += 1
        if message.content.split(' ')[0][1:] not in ["addcmd", "updcmd"]:
            message.content = await self.process_subcommands(message.content, message, user)
        command = message.content[1:].split(' ')
        command = list(filter(None, command))
        if self.perform is not None:
            return await self.perform(message, command, silent)
        elif self.message is not None:
            response = self.message
            response = response.replace("@author@", message.author.mention)
            response = response.replace("@args@", ' '.join(command[1:]))
            for i in range(len(command)):
                response = response.replace("@arg" + str(i) + "@", command[i])
            response = await self.process_subcommands(response, message, user)
            if len(response) > 0:
                if not silent:
                    for chunk in Util.split_by_chunks(response, const.DISCORD_MAX_MESSAGE_LENGTH):
                        await message.channel.send(chunk)
                return response
        else:
            await message.channel.send("Command '{}' is not callable".format(command[0]))


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
            if command[0] not in self.config.commands.data.keys():
                await self.channel.send("Unknown command '{}'".format(command[0]))
            else:
                actor = self.config.commands.data[command[0]]
                await actor.run(self.message, command, None)

    def cancel(self):
        self.task.cancel()


class Reaction:
    def __init__(self, regex, emoji):
        self.regex = regex
        self.emoji = emoji


class GuildSettings:
    def __init__(self, id):
        self.id = id
        self.is_whitelisted = False
        self.whitelist = set()
        self.markov_whitelist = set()
        self.responses_whitelist = set()
        self.reactions_whitelist = set()
        self.markov_pings = True


class User:
    def __init__(self, id):
        self.id = id
        self.permission_level = const.Permission.USER.value


class Config:
    def __init__(self):
        commands = __import__("commands", globals(), locals(), level=1)
        if not hasattr(self, "commands"):
            self.commands = commands.Commands(self)
        self.commands.update()
        if not hasattr(self, "reactions"):
            self.reactions = []
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "users"):
            self.users = dict()
        if not hasattr(self, "reminders"):
            self.reminders = []
        if not hasattr(self, "commands_prefix"):
            self.commands_prefix = "!"

    def backup(self, *files, compress=True):
        compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
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
                log.error("Unable to create backup {} -> {}: {}".format(file, backup_file, e))
            else:
                log.info("Created backup for {}: {}".format(file, backup_file))

    def save(self, config_file, markov_file, secret_config_file, wait=False):
        config_mutex = threading.Lock()
        config_mutex.acquire()
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
        config_mutex.release()
        secret_config_mutex = threading.Lock()
        secret_config_mutex.acquire()
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
        secret_config_mutex.release()
        markov_mutex = threading.Lock()
        markov_mutex.acquire()
        log.info("Saving of Markov module data is started")
        try:
            thread = threading.Thread(
                target=bc.markov.serialize,
                args=(markov_file, bc.yaml_dumper))
            thread.start()
            if wait:
                thread.join()
                log.info("Saving of Markov is waited")
        except Exception:
            log.error("Saving of Markov module data is failed", exc_info=True)
        markov_mutex.release()

    def get_version(self):
        if not os.path.exists(os.path.join(os.getcwd(), ".git")):
            return "Unable to get version (.git folder is not found)"
        if not os.path.exists(os.path.join(os.getcwd(), ".git/HEAD")):
            return "Unable to get version (.git/HEAD file is not found)"
        with open(os.path.join(os.getcwd(), ".git/HEAD")) as f:
            branch = f.readline()
            if branch[:5] != "ref: ":
                return "Unable to get version (.git/HEAD format is unknown)"
            branch = branch[5:].strip()
        if not os.path.exists(os.path.join(os.getcwd(), ".git/" + branch)):
            return "Unable to get version (.git/" + branch + " file is not found)"
        with open(os.path.join(os.getcwd(), ".git/" + branch)) as f:
            commit_hash = f.readline()
        return commit_hash[:-1]

    def get_uptime(self):
        days, remainder = divmod(
            int((datetime.datetime.now() - bc.deployment_time).total_seconds()), 24 * 3600)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        return "{}:{:02}:{:02}:{:02}".format(days, hours, minutes, seconds)

    async def disable_pings_in_response(self, message, response):
        if not self.guilds[message.channel.guild.id].markov_pings:
            while True:
                r = const.USER_ID_REGEX.search(response)
                if r is None:
                    break
                response = const.USER_ID_REGEX.sub(
                                  str(await message.guild.fetch_member(r.group(1))),
                                  response, count=1)
            response = re.sub("@everyone", "`@everyone`", response)
            response = re.sub("@here", "`@here`", response)
        return response


class SecretConfig:
    def __init__(self):
        if not hasattr(self, "token"):
            self.token = None
