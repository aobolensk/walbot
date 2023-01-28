import glob
import importlib
import inspect
import os
import sys
from typing import Any, Callable, Dict, KeysView

from src import const
from src.api.command import Command, Implementation
from src.api.execution_context import ExecutionContext
from src.api.plugin import BasePlugin
from src.executor import Executor
from src.log import log
from src.utils import Util


class PluginManager:
    def __init__(self, executor: Executor) -> None:
        self._executor = executor
        self._plugins: Dict[str, BasePlugin] = dict()
        self._plugin_modules: Dict[str, Any] = dict()
        self._plugin_functions_interface = [
            func[0] for func in inspect.getmembers(BasePlugin, inspect.isfunction)
            if not func[0].startswith('_')
        ]

    def _handle_register_error(self, module_path: str, error_message: str) -> None:
        try:
            del sys.modules[module_path]
        except Exception as e:
            log.error(f"Failed to unload Python module when plugin registration has failed. Error: {e}")
        log.error(error_message)

    def register(self, reload: bool = False) -> None:
        """Find plugins in plugins directory and register them"""
        plugin_directory = os.path.join(os.getcwd(), "src", "plugins")
        py_files = glob.glob(f"{plugin_directory}/*.py")
        py_files.extend(glob.glob(f"{plugin_directory}/*/*.py"))
        py_files.extend(glob.glob(f"{plugin_directory}/private/*/*.py"))
        plugin_modules = [Util.path_to_module(
            f"src.plugins.{os.path.splitext(os.path.relpath(file, plugin_directory))[0]}") for file in py_files]
        importlib.invalidate_caches()
        for module in plugin_modules:
            self._process_module(module, reload=reload)

    def _process_module(self, module: Any, reload: bool = True):
        log.debug2(f"Processing plugins from module: {module}")
        plugins_file = importlib.import_module(module)
        if reload:
            importlib.reload(plugins_file)
        plugins = [
            obj[1] for obj in inspect.getmembers(plugins_file, inspect.isclass)
            if (obj[1].__module__ == module) and issubclass(obj[1], BasePlugin)
        ]
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
                    self._plugin_modules[p.get_classname()] = module
                    log.debug(f"Registered plugin '{p.get_classname()}'")
                except Exception as e:
                    self._handle_register_error(
                        module, f"Failed to register plugin '{p.get_classname()}'. Error: {e}")
            else:
                self._handle_register_error(
                    module, f"Class '{p.get_classname()}' does comply with BasePlugin interface")
        elif len(plugins) > 1:
            self._handle_register_error(
                module, f"Module '{module}' have more than 1 class in it")
        else:
            self._handle_register_error(
                module, f"Module '{module}' have no classes in it")

    async def reload_plugin_interactive(self, execution_ctx: ExecutionContext, plugin_name: str) -> None:
        await self.send_command_interactive(execution_ctx, plugin_name, "close")
        self._process_module(self._plugin_modules[plugin_name], reload=True)
        await self.send_command_interactive(execution_ctx, plugin_name, "init")

    async def send_command(self, plugin_name: str, command_name: str, *args, **kwargs) -> Any:
        """Send command to specific plugin"""
        if plugin_name not in self._plugins.keys():
            return log.error(f"Unknown plugin '{plugin_name}'")
        if command_name not in self._plugin_functions_interface:
            return log.error(f"Unknown command '{command_name}' for plugin")
        if await self._plugins[plugin_name].is_enabled() or command_name in (
            "init",
            "is_enabled",
            "update_implementation",
        ):
            return await getattr(self._plugins[plugin_name], command_name)(*args, **kwargs)

    async def send_command_interactive(
            self, execution_ctx: ExecutionContext, plugin_name: str, command_name: str, *args, **kwargs) -> Any:
        try:
            return await self.send_command(plugin_name, command_name, *args, **kwargs)
        except Exception as e:
            await execution_ctx.send_message(
                f"Failed to send command '{command_name}' to plugin '{plugin_name}'. Error: {e}")

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
            await execution_ctx.send_message(f"Failed to broadcast command '{command_name}'. Error: {e}")

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
        log.debug(f"Registered bot command '{cmd_name}' for '{plugin_name}' plugin")
        self._executor.commands[cmd_name] = Command(
            "plugin_" + plugin_name, cmd_name, permission_level, Implementation.FUNCTION,
            impl_func=command_func, *args, **kwargs)
        self._executor.register_command(cmd_name, self._executor.commands[cmd_name])

    async def unregister_bot_command(
            self, plugin_name: str, cmd_name: str) -> None:
        log.debug(f"Unregistered bot command '{cmd_name}' for '{plugin_name}' plugin")
        self._executor.unregister_command(cmd_name)
