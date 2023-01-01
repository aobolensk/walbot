import datetime
import os
import re
import sys
import uuid

import yaml

from src import const
from src.api.command import Command, Implementation
from src.backend.discord.config import DiscordConfig
from src.backend.telegram.config import TelegramConfig
from src.ff import FF
from src.log import log
from src.utils import Util


class Updater:
    def __init__(self, name):
        """Dispaching config to its updater by config name"""
        self.config_name = name
        self.modified = False

    def _save_yaml_file(self, path, config):
        _, yaml_dumper = Util.get_yaml()
        with open(path, 'wb') as f:
            f.write(yaml.dump(config, Dumper=yaml_dumper, encoding='utf-8', allow_unicode=True))

    def update(self):
        """Perform update"""
        yaml_path = self.config_name + '.yaml'
        if os.path.isfile(yaml_path):
            # .yaml file path
            log.info(f"Сhecking {self.config_name} version...")
            config = Util.read_config_file(yaml_path)
            getattr(self, self.config_name + "_yaml")(config)
        else:
            log.error(f"File '{self.config_name}.yaml' does not exist")
            sys.exit(const.ExitStatus.CONFIG_FILE_ERROR)
        if self.modified:
            self._save_yaml_file(yaml_path, config)

    def result(self):
        """Get updater result: was config file actually updated or not"""
        return self.modified

    def _bump_version(self, config, new_version):
        config.version = new_version
        self.modified = True
        log.info(f"Successfully upgraded to version {new_version}")

    def config_yaml(self, config):
        """Update config.yaml"""
        if config.version == "0.0.1":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "times_called"):
                    config.commands.data[key].times_called = 0
            self._bump_version(config, "0.0.2")
        if config.version == "0.0.2":
            config.__dict__["ids"] = {"reminder": 1}
            reminders = config.reminders
            config.reminders = {}
            for reminder in reminders:
                config.reminders[config.ids["reminder"]] = reminder
                config.ids["reminder"] += 1
            self._bump_version(config, "0.0.3")
        if config.version == "0.0.3":
            for com in ("quote", "addquote", "listquote", "delquote", "setquoteauthor"):
                config.commands.data[com].module_name = "src.cmd.quote"
                config.commands.data[com].class_name = "QuoteCommands"
            for com in ("reminder", "updreminder", "listreminder", "delreminder"):
                config.commands.data[com].module_name = "src.cmd.reminder"
                config.commands.data[com].class_name = "ReminderCommands"
            self._bump_version(config, "0.0.4")
        if config.version == "0.0.4":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "cmd_line"):
                    config.commands.data[key].cmd_line = None
            self._bump_version(config, "0.0.5")
        if config.version == "0.0.5":
            for com in ("markov", "markovgc", "delmarkov", "findmarkov", "dropmarkov", "addmarkovfilter",
                        "listmarkovfilter", "delmarkovfilter"):
                config.commands.data[com].module_name = "src.cmd.markov"
                config.commands.data[com].class_name = "MarkovCommands"
            self._bump_version(config, "0.0.6")
        if config.version == "0.0.6":
            if hasattr(config.commands, "config"):
                delattr(config.commands, "config")
            self._bump_version(config, "0.0.7")
        if config.version == "0.0.7":
            config.__dict__["saving"] = {
                "backup": {
                    "compress": config.compress,
                    "period": 10,
                },
                "period": 10,
            }
            delattr(config, "compress")
            self._bump_version(config, "0.0.8")
        if config.version == "0.0.8":
            config.ids["reaction"] = 1
            reactions = config.reactions
            config.reactions = {}
            for reaction in reactions:
                config.reactions[config.ids["reaction"]] = reaction
                config.ids["reaction"] += 1
            self._bump_version(config, "0.0.9")
        if config.version == "0.0.9":
            config.__dict__["responses"] = dict()
            config.ids["response"] = 1
            self._bump_version(config, "0.0.10")
        if config.version == "0.0.10":
            for index in config.reminders.keys():
                config.reminders[index].__dict__["users"] = []
            self._bump_version(config, "0.0.11")
        if config.version == "0.0.11":
            if "addreminder" in config.commands.aliases.keys():
                del config.commands.aliases["addreminder"]
            config.commands.data["addreminder"] = config.commands.data["reminder"]
            del config.commands.data["reminder"]
            config.commands.data["addreminder"].module_name = "src.cmd.reminder"
            config.commands.data["addreminder"].perform = "_addreminder"
            self._bump_version(config, "0.0.12")
        if config.version == "0.0.12":
            for index, reminder in config.reminders.items():
                reminder.__dict__["ping_users"] = reminder.users
                del reminder.__dict__["users"]
                reminder.__dict__["whisper_users"] = []
            self._bump_version(config, "0.0.13")
        if config.version == "0.0.13":
            for guild in config.discord.guilds.values():
                guild.__dict__["markov_logging_whitelist"] = guild.markov_whitelist
                del guild.__dict__["markov_whitelist"]
                guild.__dict__["markov_responses_whitelist"] = guild.responses_whitelist
                del guild.__dict__["responses_whitelist"]
            self._bump_version(config, "0.0.14")
        if config.version == "0.0.14":
            for guild in config.discord.guilds.values():
                guild.__dict__["responses_whitelist"] = set()
            self._bump_version(config, "0.0.15")
        if config.version == "0.0.15":
            config.__dict__["repl"] = {}
            config.repl["port"] = 8080  # set default port for REPL
            self._bump_version(config, "0.0.16")
        if config.version == "0.0.16":
            for reminder in config.reminders.values():
                reminder.__dict__["repeat_after"] = 0
            self._bump_version(config, "0.0.17")
        if config.version == "0.0.17":
            config.ids["quote"] = 1
            quotes = config.quotes
            config.quotes = {}
            for quote in quotes:
                config.quotes[config.ids["quote"]] = quote
                config.ids["quote"] += 1
            self._bump_version(config, "0.0.18")
        if config.version == "0.0.18":
            for index in config.reminders.keys():
                config.reminders[index].__dict__["author"] = "<unknown>"
            self._bump_version(config, "0.0.19")
        if config.version == "0.0.19":
            for index in config.reminders.keys():
                config.reminders[index].__dict__["time_created"] = (
                    datetime.datetime(1970, 1, 1).strftime(const.REMINDER_DATETIME_FORMAT))
            self._bump_version(config, "0.0.20")
        if config.version == "0.0.20":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "is_private"):
                    config.commands.data[key].is_private = False
            self._bump_version(config, "0.0.21")
        if config.version == "0.0.21":
            for key in config.commands.data.keys():
                if (hasattr(config.commands.data[key], "module_name") and
                        not config.commands.data[key].module_name.startswith("src.")):
                    del config.commands.data[key].__dict__["module_name"]
            self._bump_version(config, "0.0.22")
        if config.version == "0.0.22":
            for index, reminder in config.reminders.items():
                reminder.__dict__["repeat_interval_measure"] = "minutes"
            self._bump_version(config, "0.0.23")
        if config.version == "0.0.23":
            for guild in config.discord.guilds.values():
                guild.__dict__["ignored"] = False
            self._bump_version(config, "0.0.24")
        if config.version == "0.0.24":
            config.commands.data["listreminder"].subcommand = False
            self._bump_version(config, "0.0.25")
        if config.version == "0.0.25":
            config.commands.data["reminder"].subcommand = False
            self._bump_version(config, "0.0.26")
        if config.version == "0.0.26":
            for index in config.quotes.keys():
                config.quotes[index].added_by = config.quotes[index].added_by[:-5]
            self._bump_version(config, "0.0.27")
        if config.version == "0.0.27":
            config.ids["timer"] = 1
            self._bump_version(config, "0.0.28")
        if config.version == "0.0.28":
            config.__dict__["plugins"] = dict()
            self._bump_version(config, "0.0.29")
        if config.version == "0.0.29":
            config.ids["stopwatch"] = 1
            self._bump_version(config, "0.0.30")
        if config.version == "0.0.30":
            for index, reminder in config.reminders.items():
                reminder.__dict__["email_users"] = []
            self._bump_version(config, "0.0.31")
        if config.version == "0.0.31":
            for index, reminder in config.reminders.items():
                reminder.__dict__["prereminders_list"] = []
            self._bump_version(config, "0.0.32")
        if config.version == "0.0.32":
            for index, reminder in config.reminders.items():
                reminder.__dict__["used_prereminders_list"] = [False] * len(reminder.prereminders_list)
            self._bump_version(config, "0.0.33")
        if config.version == "0.0.33":
            config.commands.__dict__["module_help"] = dict()
            self._bump_version(config, "0.0.34")
        if config.version == "0.0.34":
            for index, reminder in config.reminders.items():
                reminder.__dict__["notes"] = ""
            self._bump_version(config, "0.0.35")
        if config.version == "0.0.35":
            config.ids["markov_ignored_prefix"] = 1
            self._bump_version(config, "0.0.36")
        if config.version == "0.0.36":
            config.__dict__["telegram"] = {
                "channel_whitelist": set(),
                "passphrase": uuid.uuid4().hex,
            }
            self._bump_version(config, "0.0.37")
        if config.version == "0.0.37":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "max_execution_time"):
                    config.commands.data[key].max_execution_time = const.MAX_COMMAND_EXECUTION_TIME
            for cmd in (
                "poll",
                "stopwatch",
                "timer",
                "vqfpush",
                "vqpush",
                "disabletl",
                "img",
            ):
                config.commands.data[cmd].max_execution_time = -1
            config.commands.data["translate"].max_execution_time = 10
            self._bump_version(config, "0.0.38")
        if config.version == "0.0.38":
            config.__dict__["on_mention_command"] = "markov"
            self._bump_version(config, "0.0.39")
        if config.version == "0.0.39":
            config.commands.data["weather"].max_execution_time = 15
            config.commands.data["weatherforecast"].max_execution_time = 15
            self._bump_version(config, "0.0.40")
        if config.version == "0.0.40":
            config.commands.data["weather"].subcommand = True
            self._bump_version(config, "0.0.41")
        if config.version == "0.0.41":
            config.commands.data["netcheck"].max_execution_time = 60
            self._bump_version(config, "0.0.42")
        if config.version == "0.0.42":
            for index, reminder in config.reminders.items():
                reminder.__dict__["backend"] = str(const.BotBackend.DISCORD)
            self._bump_version(config, "0.0.43")
        if config.version == "0.0.43":
            for index, reminder in config.reminders.items():
                reminder.__dict__["discord_whisper_users"] = reminder.whisper_users
                del reminder.__dict__["whisper_users"]
                reminder.__dict__["telegram_whisper_users"] = []
            self._bump_version(config, "0.0.44")
        if config.version == "0.0.44":
            config.__dict__["executor"] = dict()
            config.__dict__["executor"]["commands_data"] = dict()
            self._bump_version(config, "0.0.45")
        if config.version == "0.0.45":
            config.commands.data["echo"].message = None
            config.commands.data["echo"].perform = "_echo"
            self._bump_version(config, "0.0.46")
        if config.version == "0.0.46":
            config.__dict__["discord"] = DiscordConfig()
            config.discord.guilds = config.guilds
            del config.__dict__["guilds"]
            self._bump_version(config, "0.0.47")
        if config.version == "0.0.47":
            telegram_config = TelegramConfig()
            telegram_config.channel_whitelist = config.telegram["channel_whitelist"]
            telegram_config.passphrase = config.telegram["passphrase"]
            config.__dict__["telegram"] = telegram_config
            self._bump_version(config, "0.0.48")
        if config.version == "0.0.48":
            config.discord.__dict__["users"] = config.users
            del config.__dict__["users"]
            self._bump_version(config, "0.0.49")
        if config.version == "0.0.49":
            config.telegram.__dict__["users"] = dict()
            self._bump_version(config, "0.0.50")
        if config.version == "0.0.50":
            config.commands.data["delmarkovfilter"].subcommand = False
            self._bump_version(config, "0.0.51")
        if config.version == "0.0.51":
            config.commands.data["addmarkovignoredprefix"].subcommand = False
            config.commands.data["listmarkovignoredprefix"].permission = 0
            config.commands.data["delmarkovignoredprefix"].subcommand = False
            self._bump_version(config, "0.0.52")
        if config.version == "0.0.52":
            config.executor["custom_commands"] = dict()
            for cmd_name, command in config.commands.data.items():
                if command.cmd_line is not None:
                    config.executor["custom_commands"][cmd_name] = Command(
                        None, cmd_name, command.permission, Implementation.EXTERNAL_CMDLINE,
                        subcommand=True, impl_message=command.cmd_line)
            self._bump_version(config, "0.0.53")
        if config.version == "0.0.53":
            config.commands.data["getmarkovword"].subcommand = True
            self._bump_version(config, "0.0.54")
        if config.version == "0.0.54":
            for index in config.reminders.keys():
                config.reminders[index].__dict__["remaining_repetitions"] = -1
            self._bump_version(config, "0.0.55")
        if config.version == "0.0.55":
            for index in config.reminders.keys():
                config.reminders[index].__dict__["limit_repetitions_time"] = None
            self._bump_version(config, "0.0.56")
        if config.version == "0.0.56":
            config.commands.data["dbg"].subcommand = True
            self._bump_version(config, "0.0.57")
        if config.version == "0.0.56":
            log.info(f"Version of {self.config_name} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_name}!")

    def markov_yaml(self, config):
        """Update markov.yaml"""
        if config.version == "0.0.1":
            config.__dict__["min_chars"] = 1
            config.__dict__["min_words"] = 1
            self._bump_version(config, "0.0.2")
        if config.version == "0.0.2":
            config.__dict__["chains_generated"] = 0
            self._bump_version(config, "0.0.3")
        if config.version == "0.0.3":
            config.__dict__["max_chars"] = 2000
            config.__dict__["max_words"] = 500
            self._bump_version(config, "0.0.4")
        if config.version == "0.0.4":
            config.model[""].__dict__["word"] = None
            self._bump_version(config, "0.0.5")
        if config.version == "0.0.5":
            for i, _ in enumerate(config.filters):
                config.__dict__["filters"][i] = re.compile(config.filters[i].pattern, re.DOTALL)
            self._bump_version(config, "0.0.6")
        if config.version == "0.0.6":
            config.__dict__["ignored_prefixes"] = dict()
            self._bump_version(config, "0.0.7")
        if config.version == "0.0.7":
            if FF.is_enabled("WALBOT_FEATURE_MARKOV_MONGO") == "1":
                from src.db.walbot_db import WalbotDatabase
                db = WalbotDatabase()

                def preprocess_key(key: str):
                    return key.replace("$", "<__markov_dollar>").replace(".", "<__markov_dot>")

                markov_model = dict()
                for key, value in config.model.items():
                    if key is None or key == "":
                        key = "__markov_null"
                    next_list = dict()
                    for k, v in value.next.items():
                        if k is None:
                            k = "__markov_terminate"
                        next_list[preprocess_key(k)] = v
                    markov_model[preprocess_key(key)] = {
                        "word": value.word,
                        "next": next_list,
                        "total_next": value.total_next,
                        "type": value.type,
                    }
                markov_ignored_prefixes = dict()
                for key, value in config.ignored_prefixes.items():
                    markov_ignored_prefixes[str(key)] = value
                db.markov.insert({
                    "chains_generated": config.chains_generated,
                    "end_node": {
                        "word": None,
                        "next": {
                            "__markov_null": 0,
                        },
                        "total_next": 0,
                        "type": 2,
                    },
                    "filters": config.filters,
                    "ignored_prefixes": markov_ignored_prefixes,
                    "max_chars": config.max_chars,
                    "max_words": config.max_words,
                    "min_chars": config.min_chars,
                    "min_words": config.min_words,
                    "model": markov_model,
                    "version": "0.1.0",
                })
                self._bump_version(config, "0.1.0")
                log.warning("Markov model has been moved to MongoDB!")
                return
            log.info(f"Version of {self.config_name} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_name}!")

    def secret_yaml(self, config):
        """Update secret.yaml"""
        if config.version == "0.0.1":
            config.__dict__["mail"] = {
                "smtp_server": None,
                "email": None,
                "password": None,
            }
            config.__dict__["admin_email_list"] = list()
            self._bump_version(config, "0.0.2")
        if config.version == "0.0.2":
            config.__dict__["telegram"] = dict()
            config.__dict__["telegram"]["token"] = None
            self._bump_version(config, "0.0.3")
        if config.version == "0.0.3":
            config.__dict__["discord"] = dict()
            config.__dict__["discord"]["token"] = config.__dict__["token"]
            del config.__dict__["token"]
            self._bump_version(config, "0.0.4")
        if config.version == "0.0.4":
            log.info(f"Version of {self.config_name} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_name}!")

    def secret_db(self):
        """Update db/secret.db"""
        pass
