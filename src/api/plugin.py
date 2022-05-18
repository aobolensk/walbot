from abc import abstractmethod

import discord


class BasePlugin:
    """WalBot plugin interface"""
    @classmethod
    def get_classname(cls):
        return cls.__name__

    def __init__(self) -> None:
        self._enabled = False

    # Plugin interface:

    async def is_enabled(self) -> bool:
        """Get plugin initialization state"""
        return self._enabled

    @abstractmethod
    async def init(self) -> None:
        """Executes when plugin was loaded"""
        self._enabled = True

    @abstractmethod
    async def on_message(self, message: discord.Message) -> None:
        """Executes when message was sent"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Executes when plugin was unloaded"""
        self._enabled = False
