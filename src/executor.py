from typing import Any, Dict

from src.api.command import BaseCmd


class Executor:
    def __init__(self) -> None:
        self.commands = {}

    def add_module(self, module: BaseCmd) -> None:
        module.bind()

    def load_persistent_state(self, commands_data: Dict[str, Any]):
        for command in self.commands.values():
            command.load_persistent_state(commands_data)

    def store_persistent_state(self, commands_data: Dict[str, Any]):
        for command in self.commands.values():
            command.store_persistent_state(commands_data)
