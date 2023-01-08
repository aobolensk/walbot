import importlib
import inspect
import os
from typing import Any, Callable, Dict, KeysView

from src import const
from src.api.command import Command, Implementation
from src.api.execution_context import ExecutionContext
from src.api.plugin import BasePlugin
from src.log import log
from src.utils import Util


class PluginManager:
    def __init__(self) -> None:
        self._plugins: Dict[str, BasePlugin] = dict()
        self._plugin_functions_interface = [
            func[0] for func in inspect.getmembers(BasePlugin, inspect.isfunction)
            if not func[0].startswith('_')
        ]

    def register(self, reload: bool = False) -> None:
        """Find plugins in plugins directory and register them"""
        plugin_directory = os.path.join(os.getcwd(), "src", "plugins")
        plugin_modules = [Util.path_to_module(
            f"src.plugins.{os.path.relpath(path, plugin_directory)}."
            f"{os.path.splitext(file)[0]}")
            for path, _, files in os.walk(plugin_directory) for file in files
            if os.path.isfile(os.path.join(plugin_directory, path, file)) and file.endswith(".py")]
        importlib.invalidate_caches()
        for module in plugin_modules:
            log.debug2(f"Processing plugins from module: {module}")
            plugins_file = importlib.import_module(module)
            if reload:
                importlib.reload(plugins_file)
            plugins = [obj[1] for obj in inspect.getmembers(plugins_file, inspect.isclass)
                       if (obj[1].__module__ == module) and issubclass(obj[1], BasePlugin)]
            if len(plugins) == 1:
                plugin = plugins[0]
                actual_functions_list = [
                    func[0] for func in inspect.getmembers(plugin, inspect.isfunction)
                    if not func[0].startswith('_')
                ]
                if all(x in actual_functions_list for x in self._plugin_functions_interface):
                    try:
                        p = plugin()
                        self._plugins[p.get_classname()] = p
                        log.debug(f"Registered plugin '{p.get_classname()}'")
                    except Exception as e:
                        log.error(f"Failed to register plugin '{p.get_classname()}'. Error: {e}")
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

    async def send_command_interactive(
            self, execution_ctx: ExecutionContext, plugin_name: str, command_name: str, *args, **kwargs) -> Any:
        try:
            return await self.send_command(plugin_name, command_name, *args, **kwargs)
        except Exception as e:
            execution_ctx.send_message(f"Failed to send command '{command_name}' to plugin '{plugin_name}'. Error: {e}")

    async def broadcast_command(self, command_name: str, *args, **kwargs) -> None:
        """Broadcast command for all plugins"""
        if command_name not in self._plugin_functions_interface:
            return log.error(f"Unknown command '{command_name}' for plugin")
        for plugin_name in self._plugins.keys():
            if await self._plugins[plugin_name].is_enabled() or command_name == "init":
                await getattr(self._plugins[plugin_name], command_name)(*args, **kwargs)

    async def broadcast_command_interactive(
            self, execution_ctx: ExecutionContext, command_name: str, *args, **kwargs) -> None:
        try:
            return await self.broadcast_command(command_name, *args, **kwargs)
        except Exception as e:
            execution_ctx.send_message(f"Failed to broadcast command '{command_name}'. Error: {e}")

    def get_plugins_list(self) -> KeysView[str]:
        """Get list of plugin names that were registered"""
        return self._plugins.keys()

    async def load_plugins(self) -> None:
        bc = importlib.import_module("src.config").bc
        for plugin_name in self.get_plugins_list():
            if plugin_name not in bc.config.plugins.keys():
                bc.config.plugins[plugin_name] = {
                    "autostart": False,
                }
        for plugin_name, plugin_state in bc.config.plugins.items():
            if plugin_state["autostart"]:
                try:
                    await self.send_command(plugin_name, "init")
                except Exception as e:
                    log.error(f"Failed to run 'init' command for plugin '{plugin_name}'. Error: {e}")

    async def unload_plugins(self) -> None:
        for plugin_name in self.get_plugins_list():
            try:
                if await self.send_command(plugin_name, "is_enabled"):
                    await self.send_command(plugin_name, "close")
            except Exception as e:
                log.error(f"Failed to run 'close' command for plugin '{plugin_name}'. Error: {e}")

    async def register_bot_command(
            self, plugin_name: str, cmd_name: str, permission_level: const.Permission,
            command_func: Callable, *args, **kwargs) -> None:
        from src.config import bc
        log.debug(f"Registered bot command '{cmd_name}' for '{plugin_name}' plugin")
        bc.executor.commands[cmd_name] = Command(
            "plugin_" + plugin_name, cmd_name, permission_level, Implementation.FUNCTION,
            impl_func=command_func, *args, **kwargs)
        bc.executor.register_command(cmd_name, bc.executor.commands[cmd_name])

    async def unregister_bot_command(
            self, plugin_name: str, cmd_name: str) -> None:
        from src.config import bc
        log.debug(f"Unregistered bot command '{cmd_name}' for '{plugin_name}' plugin")
        bc.executor.unregister_command(cmd_name)
