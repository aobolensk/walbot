"""log.py
Contains definition of WalBot logger and instance of the logger
"""

import functools
import inspect
import logging
import logging.config
import os
from typing import Any

from src import const


class Log:
    """WalBot logger
    Proper usage: the single object of this class defined below class definition
    """

    def debug2(self, msg: str, *args, **kwargs) -> None:
        """Log with severity 'DEBUG2'."""
        self.log.log(const.LogLevel.DEBUG2, msg, *args, **kwargs)

    def debug3(self, msg: str, *args, **kwargs) -> None:
        """Log with severity 'DEBUG3'."""
        self.log.log(const.LogLevel.DEBUG3, msg, *args, **kwargs)

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
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
        formatter = logging.Formatter(const.LOGGING_FORMAT)
        # HANDLERS
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(const.LogLevel.DEBUG)  # Change console logging level for debugging on this line
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

    def trace_function(self, func) -> Any:
        """Tracing enter and exit events for functions. It should be used as a decorator"""
        if inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def wrapped(*args):
                self.debug(f"Function '{func.__name__}' (ENTER)")
                ret = await func(*args)
                self.debug(f"Function '{func.__name__}' (EXIT)")
                return ret
            return wrapped
        else:
            def inner(*args, **kwargs):
                self.debug(f"Function '{func.__name__}' (ENTER)")
                ret = func(*args, **kwargs)
                self.debug(f"Function '{func.__name__}' (EXIT)")
                return ret
            return inner

    class trace_block:  # pylint: disable=invalid-name
        """Tracing enter and exit events for blocks of code. It should be used as a context manager"""

        def __init__(self, name) -> None:
            self._name = name
            log.debug(f"Block '{name}' (ENTER)")

        def __enter__(self) -> None:
            pass

        def __exit__(self, type, value, traceback) -> None:
            log.debug(f"Block '{self._name}' (EXIT)")


# Use this logger instance for logging everywhere
log = Log()
