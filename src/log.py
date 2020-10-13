import logging
import logging.config
import os

from src import const


class Log:
    def debug2(self, msg, *args, **kwargs):
        """Log with severity 'DEBUG2'."""
        self.log.log(const.LogLevel.DEBUG2, msg, *args, **kwargs)

    def debug3(self, msg, *args, **kwargs):
        """Log with severity 'DEBUG3'."""
        self.log.log(const.LogLevel.DEBUG3, msg, *args, **kwargs)

    def __init__(self):
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })
        # Add new logging levels
        logging.addLevelName(const.LogLevel.DEBUG2, "DEBUG2")
        logging.addLevelName(const.LogLevel.DEBUG3, "DEBUG3")
        # LOGGERS
        self.log = logging.getLogger("WalBot")
        self.log.setLevel(const.LogLevel.DEBUG3)
        # FORMATTERS
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        # HANDLERS
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(const.LogLevel.DEBUG3)
        console_handler.setFormatter(formatter)
        self.log.addHandler(console_handler)
        # Create logs folder
        if not os.path.exists(const.LOGS_DIRECTORY):
            os.makedirs(const.LOGS_DIRECTORY)
        # File handler (logs/error.log)
        err_log_file_hdl = logging.handlers.RotatingFileHandler(
            os.path.join(const.LOGS_DIRECTORY, "error.log"), encoding="utf-8",
            maxBytes=const.MAX_LOG_FILESIZE, backupCount=20)
        err_log_file_hdl.setLevel(const.LogLevel.ERROR)
        err_log_file_hdl.setFormatter(formatter)
        self.log.addHandler(err_log_file_hdl)
        # File handler (logs/walbot.log)
        general_log_file_hdl = logging.handlers.RotatingFileHandler(
            os.path.join(const.LOGS_DIRECTORY, "walbot.log"), encoding="utf-8",
            maxBytes=const.MAX_LOG_FILESIZE, backupCount=20)
        general_log_file_hdl.setLevel(const.LogLevel.DEBUG)
        general_log_file_hdl.setFormatter(formatter)
        self.log.addHandler(general_log_file_hdl)
        # Add basic log functions
        self.debug = self.log.debug
        self.info = self.log.info
        self.error = self.log.error
        self.warning = self.log.warning
        self.info("Logging system is set up")


log = Log()
