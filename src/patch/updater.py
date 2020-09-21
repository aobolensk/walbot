import os

from ..log import log


class Updater:
    def __init__(self, path, config):
        """Dispaching config to its updater by config name"""
        self.config_path = path
        self.modified = False
        getattr(self, os.path.splitext(path)[0])(config)

    def result(self):
        return self.modified

    def _bump_version(self, config, new_version):
        config.version = new_version
        self.modified = True
        log.info(f"Successfully upgraded to version {new_version}")

    def config(self, config):
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
            log.info(f"Version of {self.config_path} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_path}!")

    def markov(self, config):
        if config.version == "0.0.1":
            config.__dict__["min_chars"] = 1
            config.__dict__["min_words"] = 1
            self._bump_version(config, "0.0.2")
        if config.version == "0.0.2":
            log.info(f"Version of {self.config_path} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_path}!")

    def secret(self, config):
        if config.version == "0.0.1":
            log.info(f"Version of {self.config_path} is up to date!")
        else:
            log.error(f"Unknown version {config.version} for {self.config_path}!")
