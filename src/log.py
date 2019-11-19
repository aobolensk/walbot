import logging
import logging.config


class Log:
    def __init__(self):
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
        })
        self.log = logging.getLogger("WalBot")
        self.log.setLevel(logging.DEBUG)
        fh = logging.FileHandler("log.txt")
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.log.addHandler(fh)
        self.log.addHandler(ch)
        self.debug = self.log.debug
        self.info = self.log.info
        self.error = self.log.error
        self.info("Logging system is set up")


log = Log()
