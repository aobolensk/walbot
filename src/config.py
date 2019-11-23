import asyncio
import datetime
import os
import shutil
import threading
import yaml

from .log import log


class RuntimeConfig:
    def __init__(self):
        self.background_events = []
        self.background_loop = None
        self.deployment_time = datetime.datetime.now()


class BotWrapper():
    pass


runtime_config = RuntimeConfig()
bot_wrapper = BotWrapper()


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

    async def process_subcommands(self, response, message, user):
        percent_pos = -1
        for i in range(len(response)):
            if response[i] == '%' and (i == 0 or response[i-1] != '\\'):
                if percent_pos == -1:
                    percent_pos = i
                else:
                    message.content = response[percent_pos + 1:i]
                    command = message.content.split()
                    result = ""
                    if len(command) > 0 and command[0] in runtime_config.commands.data.keys():
                        log.debug("Processing subcommand: {}: {}".format(command[0], message.content))
                        actor = runtime_config.commands.data[command[0]]
                        result = await actor.run(message, command, user, silent=True)
                        if result is None:
                            result = ""
                    response = response[:percent_pos] + result + response[i + 1:]
                    return (response, False)
        return (response, True)

    async def run(self, message, command, user, silent=False):
        log.debug("Processing command: {}".format(message.content))
        if not self.is_available(message.channel.id):
            await message.channel.send("Command '{}' is not available in this channel".format(command[0]))
            return
        if user is not None and self.permission > user.permission_level:
            await message.channel.send("You don't have permission to call command '{}'".format(command[0]))
            return
        if self.perform is not None:
            return await self.perform(message, command, silent)
        elif self.message is not None:
            response = self.message
            response = response.replace("@author@", message.author.mention)
            response = response.replace("@args@", ' '.join(command[1:]))
            for i in range(len(command)):
                response = response.replace("@arg" + str(i) + "@", command[i])
            while True:
                response, done = await self.process_subcommands(response, message, user)
                if done:
                    break
            response = response.replace("\\%", "%")
            if (len(response.strip()) > 0):
                if not silent:
                    await message.channel.send(response)
                return response
        else:
            await message.channel.send("Command '{}' is not callable".format(command[0]))


class BackgroundEvent:
    def __init__(self, config, channel, message, period):
        self.config = config
        self.channel = channel
        self.message = message
        self.period = period
        self.task = bot_wrapper.background_loop.create_task(self.run())

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
        self.reactions_whitelist = set()


class User:
    def __init__(self, id):
        self.id = id
        self.permission_level = 0


class Config:
    def __init__(self):
        commands = __import__("commands", globals(), locals(), level=1)
        if not hasattr(self, "commands"):
            self.commands = commands.Commands(self)
        self.commands.update_builtins()
        if not hasattr(self, "reactions"):
            self.reactions = []
        if not hasattr(self, "token"):
            self.token = None
        if not hasattr(self, "guilds"):
            self.guilds = dict()
        if not hasattr(self, "users"):
            self.users = dict()
        if not hasattr(self, "commands_prefix"):
            self.commands_prefix = "!"

    def backup(self, *files):
        for file in files:
            path = os.path.dirname(file)
            name, ext = os.path.splitext(os.path.basename(file))
            name += "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = os.path.join(path, "backup", name + ext)
            if not os.path.exists("backup"):
                os.makedirs("backup")
            try:
                shutil.copy(file, backup_file)
            except IOError as e:
                log.error("Unable to copy {} -> {}: {}".format(file, backup_file, e))
            else:
                log.info("Created backup for {}: {}".format(file, backup_file))

    def save(self, config_file, markov_file, wait=False):
        config_mutex = threading.Lock()
        config_mutex.acquire()
        log.info("Saving of config is started")
        with open(config_file, 'wb') as f:
            try:
                f.write(yaml.dump(
                    self,
                    Dumper=runtime_config.yaml_dumper,
                    encoding='utf-8',
                    allow_unicode=True))
                log.info("Saving of config is finished")
            except Exception:
                log.error("yaml.dump failed", exc_info=True)
        config_mutex.release()
        markov_mutex = threading.Lock()
        markov_mutex.acquire()
        log.info("Saving of Markov module data is started")
        try:
            thread = threading.Thread(
                target=runtime_config.markov.serialize,
                args=(markov_file, runtime_config.yaml_dumper))
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
