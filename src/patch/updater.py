import datetime
import importlib
import os
import re
import sys

import yaml

from src import const
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
            config = Util.read_config_file(yaml_path)
            getattr(self, self.config_name + "_yaml")(config)
        else:
            if FF.is_enabled("WALBOT_FEATURE_NEW_CONFIG") == "1":
                getattr(self, self.config_name + "_db")()
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
            for guild in config.guilds.values():
                guild.__dict__["markov_logging_whitelist"] = guild.markov_whitelist
                del guild.__dict__["markov_whitelist"]
                guild.__dict__["markov_responses_whitelist"] = guild.responses_whitelist
                del guild.__dict__["responses_whitelist"]
            self._bump_version(config, "0.0.14")
        if config.version == "0.0.14":
            for guild in config.guilds.values():
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
            for guild in config.guilds.values():
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
            log.info(f"Version of {self.config_name} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_name}!")

    def secret_yaml(self, config):
        """Update secret.yaml"""
        if config.version == "0.0.1":
            if FF.is_enabled("WALBOT_FEATURE_NEW_CONFIG") == "1":
                os.makedirs("db", exist_ok=True)
                sqlite3 = importlib.import_module("sqlite3")
                con = sqlite3.connect(os.path.join("db", "secret.db"))
                cur = con.cursor()
                cur.execute("CREATE TABLE db_info (key text, value text)")
                cur.execute("INSERT INTO db_info VALUES ('version', '0.1.0')")
                cur.execute("CREATE TABLE tokens (key text, value text)")
                cur.execute("INSERT INTO tokens VALUES ('discord', ?)", (config.token,))
                con.commit()
                con.close()
                os.remove(self.config_name + '.yaml')
                log.info("Successfully migrated contig.yaml to db/config.db!")
            else:
                config.__dict__["mail"] = {
                    "smtp_server": None,
                    "email": None,
                    "password": None,
                }
                config.__dict__["admin_email_list"] = list()
                self._bump_version(config, "0.0.2")
        if config.version == "0.0.2":
            log.info(f"Version of {self.config_name} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_name}!")

    def secret_db(self):
        """Update db/secret.db"""
        pass
