from typing import Any, Dict


class DiscordConfig:
    def __init__(self) -> None:
        self.guilds: Dict[int, Any] = dict()
        self.users: Dict[int, Any] = dict()
