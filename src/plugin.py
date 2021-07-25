import importlib
import inspect
import os
from abc import abstractmethod
from typing import Any, Dict, KeysView

import discord

from src.log import log
from src.utils import Util


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


class PluginManager:
    def __init__(self) -> None:
        self._plugins: Dict[str, BasePlugin] = dict()
        self._plugin_functions_interface = [
            func[0] for func in inspect.getmembers(BasePlugin, inspect.isfunction)
            if not func[0].startswith('_')
        ]

    def register(self) -> None:
        """Find plugins in plugins directory and register them"""
        plugin_directory = os.path.join(os.path.dirname(__file__), "plugins")
        plugin_modules = ['src.plugins.' + os.path.splitext(path)[0] for path in os.listdir(plugin_directory)
                          if os.path.isfile(os.path.join(plugin_directory, path)) and path.endswith(".py")]
        private_plugin_directory = os.path.join(os.path.dirname(__file__), "plugins", "private")
        plugin_modules += [Util.path_to_module(
            f"src.plugins.private.{os.path.relpath(path, private_plugin_directory)}."
            f"{os.path.splitext(file)[0]}")
            for path, _, files in os.walk(private_plugin_directory) for file in files
            if os.path.isfile(os.path.join(private_plugin_directory, path, file)) and file.endswith(".py")]
        for module in plugin_modules:
            log.debug2(f"Processing plugins from module: {module}")
            plugins_file = importlib.import_module(module)
            plugins = [obj[1] for obj in inspect.getmembers(plugins_file, inspect.isclass)
                       if (obj[1].__module__ == module) and issubclass(obj[1], BasePlugin)]
            if len(plugins) == 1:
                plugin = plugins[0]
                actual_functions_list = [
                    func[0] for func in inspect.getmembers(plugin, inspect.isfunction)
                    if not func[0].startswith('_')
                ]
                if all(x in actual_functions_list for x in self._plugin_functions_interface):
                    p = plugin()
                    self._plugins[p.get_classname()] = p
                    log.debug(f"Registered plugin '{p.get_classname()}'")
                else:
                    log.error(f"Class '{p.get_classname()}' does comply with BasePlugin interface")
            elif len(plugins) > 1:
                log.error(f"Module '{module}' have more than 1 class in it")
            else:
                log.error(f"Module '{module}' have no classes in it")

    async def send_command(self, plugin_name: str, command_name: str, *args, **kwargs) -> Any:
        """Send command to specific plugin"""
        if plugin_name not in self._plugins.keys():
            return log.error(f"Unknown plugin '{plugin_name}'")
        if command_name not in self._plugin_functions_interface:
            return log.error(f"Unknown command '{command_name}' for plugin")
        if await self._plugins[plugin_name].is_enabled() or command_name == "init":
            return await getattr(self._plugins[plugin_name], command_name)(*args, **kwargs)

    async def broadcast_command(self, command_name: str, *args, **kwargs) -> None:
        """Broadcast command for all plugins"""
        if command_name not in self._plugin_functions_interface:
            return log.error(f"Unknown command '{command_name}' for plugin")
        for plugin_name in self._plugins.keys():
            if await self._plugins[plugin_name].is_enabled() or command_name == "init":
                await getattr(self._plugins[plugin_name], command_name)(*args, **kwargs)


    def get_plugins_list(self) -> KeysView[str]:
        """Get list of plugin names that were registered"""
        return self._plugins.keys()
