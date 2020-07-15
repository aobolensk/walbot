import os

from ..log import log


class Updater:
    def __init__(self, path, config):
        """Dispaching config to its updater by config name"""
        self.modified = False
        getattr(self, os.path.splitext(path)[0])(config)

    def result(self):
        return self.modified

    def config(self, config):
        if config.version == "0.0.1":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "times_called"):
                    config.commands.data[key].times_called = 0
            config.version = "0.0.2"
            self.modified = True
            log.info("Successfully upgraded your config.yaml to version 0.0.2")
        if config.version == "0.0.2":
            config.__dict__["ids"] = {"reminder": 1}
            reminders = config.reminders
            config.reminders = {}
            for reminder in reminders:
                config.reminders[config.ids["reminder"]] = reminder
                config.ids["reminder"] += 1
            config.version = "0.0.3"
            self.modified = True
            log.info("Successfully upgraded your config.yaml to version 0.0.3")
        if config.version == "0.0.3":
            for com in ("quote", "addquote", "listquote", "delquote", "setquoteauthor"):
                config.commands.data[com].module_name = "src.cmd.quote"
                config.commands.data[com].class_name = "QuoteCommands"
            for com in ("reminder", "updreminder", "listreminder", "delreminder"):
                config.commands.data[com].module_name = "src.cmd.reminder"
                config.commands.data[com].class_name = "ReminderCommands"
            config.version = "0.0.4"
            self.modified = True
            log.info("Successfully upgraded your config.yaml to version 0.0.4")
        if config.version == "0.0.4":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "cmd_line"):
                    config.commands.data[key].cmd_line = None
            config.version = "0.0.5"
            self.modified = True
            log.info("Successfully upgraded your config.yaml to version 0.0.5")
        if config.version == "0.0.5":
            for com in ("markov", "markovgc", "delmarkov", "findmarkov", "dropmarkov", "addmarkovfilter",
                        "listmarkovfilter", "delmarkovfilter"):
                config.commands.data[com].module_name = "src.cmd.markov"
                config.commands.data[com].class_name = "MarkovCommands"
            config.version = "0.0.6"
            self.modified = True
            log.info("Successfully upgraded your config.yaml to version 0.0.6")
        if config.version == "0.0.6":
            log.info("Version is up to date!")
        else:
            log.error("Unknown version {}!".format(config.version))

    def markov(self, config):
        if config.version == "0.0.1":
            log.info("Version is up to date!")
        else:
            log.error("Unknown version {}!".format(config.version))

    def secret(self, config):
        if config.version == "0.0.1":
            log.info("Version is up to date!")
        else:
            log.error("Unknown version {}!".format(config.version))
