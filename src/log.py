import logging
import logging.config
import os


class Log:
    # Logging levels: https://docs.python.org/3/library/logging.html#logging-levels
    CRITICAL: int = 50
    ERROR: int = 40
    WARNING: int = 30
    INFO: int = 20
    DEBUG: int = 10
    DEBUG2: int = 9
    NOTSET: int = 0

    def debug2(self, msg, *args, **kwargs):
        self.log.log(self.DEBUG2, msg, *args, **kwargs)

    def __init__(self):
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })
        logging.addLevelName(9, "DEBUG2")
        self.log = logging.getLogger("WalBot")
        self.log.setLevel(self.DEBUG2)
        # FORMATTERS
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        # HANDLERS
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.DEBUG)
        console_handler.setFormatter(formatter)
        self.log.addHandler(console_handler)
        # File handler (logs/error.log)
        err_log_file_hdl = logging.FileHandler(os.path.join("logs", "error.log"), encoding="utf-8")
        err_log_file_hdl.setLevel(self.ERROR)
        err_log_file_hdl.setFormatter(formatter)
        self.log.addHandler(err_log_file_hdl)
        # File handler (logs/walbot.log)
        general_log_file_hdl = logging.FileHandler(os.path.join("logs", "walbot.log"), encoding="utf-8")
        general_log_file_hdl.setLevel(self.DEBUG)
        general_log_file_hdl.setFormatter(formatter)
        self.log.addHandler(general_log_file_hdl)
        # Add basic log functions
        self.debug = self.log.debug
        self.info = self.log.info
        self.error = self.log.error
        self.warning = self.log.warning
        self.info("Logging system is set up")


log = Log()
