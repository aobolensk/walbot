from typing import Any, Dict


class DiscordConfig:
    def __init__(self) -> None:
        self.guilds: Dict[str, Any] = dict()
        self.users: Dict[str, Any] = dict()
