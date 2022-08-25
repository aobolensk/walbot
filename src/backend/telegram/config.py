import uuid


class TelegramConfig:
    def __init__(self) -> None:
        self.channel_whitelist = set()
        self.passphrase = uuid.uuid4().hex
        self.users = dict()
