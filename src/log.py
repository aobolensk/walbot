import logging
import logging.config


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
        # File handler (log.txt)
        log_file_handler = logging.FileHandler("log.txt", encoding="utf-8")
        log_file_handler.setLevel(self.DEBUG)
        log_file_handler.setFormatter(formatter)
        self.log.addHandler(log_file_handler)
        # Add basic log functions
        self.debug = self.log.debug
        self.info = self.log.info
        self.error = self.log.error
        self.warning = self.log.warning
        self.info("Logging system is set up")


log = Log()
