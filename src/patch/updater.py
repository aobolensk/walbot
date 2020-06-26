import os

from ..log import log


class Updater:
    def __init__(self, path, config):
        """Dispaching config to its updater by config name"""
        getattr(self, os.path.splitext(path)[0])(config)

    def config(self, config):
        if config.version == "0.0.1":
            for key in config.commands.data.keys():
                if not hasattr(config.commands.data[key], "times_called"):
                    config.commands.data[key].times_called = 0
            config.version = "0.0.2"
            log.info("Successfully upgraded your config.yaml to version 0.0.2")
        elif config.version == "0.0.2":
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
