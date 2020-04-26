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
        fh = logging.FileHandler("log.txt", encoding="utf-8")
        ch = logging.StreamHandler()
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        for h in (fh, ch):
            h.setLevel(logging.DEBUG)
            h.setFormatter(formatter)
            self.log.addHandler(h)
        self.debug = self.log.debug
        self.info = self.log.info
        self.error = self.log.error
        self.warning = self.log.warning
        self.info("Logging system is set up")


log = Log()
