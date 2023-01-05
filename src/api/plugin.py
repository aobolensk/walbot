from abc import abstractmethod

from src.api.execution_context import ExecutionContext


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
    async def on_message(self, execution_ctx: ExecutionContext) -> None:
        """Executes when message was sent"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Executes when plugin was unloaded"""
        self._enabled = False

    async def update_implementation(self) -> None:
        """Update plugin implementation. This method should execute command or sequence of commands
        that will update plugin source code files in src/plugins or src/plugins/private directory.
        Implementation is not needed if plugin is not going to support self-update feature and
        should be updated manually.
        In plugin implementation override this method and do NOT call super().update_implementation()
        """
        raise NotImplementedError
