"""WalBot plugin system management"""

from typing import List

from src import const
from src.api.command import Command, Implementation, SupportedPlatforms
from src.api.execution_context import ExecutionContext
from src.backend.discord.embed import DiscordEmbed
from src.commands import BaseCmd
from src.config import bc


class PluginCommands(BaseCmd):
    def bind(self):
        bc.executor.commands["listplugin"] = Command(
            "plugin", "listplugin", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listplugin,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["loadplugin"] = Command(
            "plugin", "loadplugin", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._loadplugin,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["reloadpluginmanager"] = Command(
            "plugin", "reloadpluginmanager", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._reloadpluginmanager,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["unloadplugin"] = Command(
            "plugin", "unloadplugin", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._unloadplugin,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["reloadplugin"] = Command(
            "plugin", "reloadplugin", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._reloadplugin,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["autostartplugin"] = Command(
            "plugin", "autostartplugin", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._autostartplugin,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))

    async def _listplugin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of plugins
    Usage:
        !listplugin"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        plugin_names = bc.plugin_manager.get_plugins_list()
        if execution_ctx.platform == const.BotBackend.DISCORD:
            e = DiscordEmbed()
            e.title("List of plugins")
            for plugin_name in plugin_names:
                is_enabled = await bc.plugin_manager.send_command(plugin_name, "is_enabled")
                e.add_field(plugin_name, "enabled" if is_enabled else "disabled", True)
            await Command.send_message(execution_ctx, None, embed=e.get())
        else:
            result = "List of plugins:\n"
            for plugin_name in plugin_names:
                is_enabled = await bc.plugin_manager.send_command(plugin_name, "is_enabled")
                is_enabled = "enabled" if is_enabled else "disabled"
                result += f"plugin_name: {is_enabled}\n"
            await Command.send_message(execution_ctx, result)

    async def _loadplugin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Load plugin by its name
    Usage:
        !loadplugin <plugin_name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        plugin_name = cmd_line[1]
        if plugin_name not in bc.plugin_manager.get_plugins_list():
            return await Command.send_message(execution_ctx, f"Could not find plugin '{plugin_name}'")
        await bc.plugin_manager.send_command(plugin_name, "init")
        await Command.send_message(execution_ctx, f"Plugin '{plugin_name}' has been loaded")

    async def _reloadpluginmanager(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Reload plugin manager
    Usage: !reloadpluginmanager"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        await bc.plugin_manager.unload_plugins()
        bc.plugin_manager.register(reload=True)
        await bc.plugin_manager.load_plugins()
        await Command.send_message(execution_ctx, "Plugin manager has been reloaded")

    async def _unloadplugin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Unload plugin by its name
    Usage:
        !unloadplugin <plugin_name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        plugin_name = cmd_line[1]
        if plugin_name not in bc.plugin_manager.get_plugins_list():
            return await Command.send_message(execution_ctx, f"Could not find plugin '{plugin_name}'")
        await bc.plugin_manager.send_command(plugin_name, "close")
        await Command.send_message(execution_ctx, f"Plugin '{plugin_name}' has been unloaded")

    async def _reloadplugin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Reload plugin by its name
    Usage:
        !reloadplugin <plugin_name>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        plugin_name = cmd_line[1]
        if plugin_name not in bc.plugin_manager.get_plugins_list():
            return await Command.send_message(execution_ctx, f"Could not find plugin '{plugin_name}'")
        await bc.plugin_manager.send_command(plugin_name, "close")
        await bc.plugin_manager.send_command(plugin_name, "init")
        await Command.send_message(execution_ctx, f"Plugin '{plugin_name}' has been reloaded")

    async def _autostartplugin(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Check if plugin automatically starts when bot loads up and set autostart flag for plugin
    Usage:
        !autostartplugin <plugin_name>          <- check if autostart is enabled
        !autostartplugin <plugin_name> enable   <- enable autostart for plugin
        !autostartplugin <plugin_name> disable  <- disable autostart for plugin"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=3):
            return
        plugin_name = cmd_line[1]
        if len(cmd_line) == 2:
            if plugin_name not in bc.config.plugins.keys():
                return await Command.send_message(execution_ctx, f"Could not find plugin '{plugin_name}'")
            is_enabled = bc.config.plugins[plugin_name]["autostart"]
            await Command.send_message(
                execution_ctx, f"Autostart for plugin '{plugin_name}' is '{'enabled' if is_enabled else 'disabled'}'")
        else:  # len == 3
            cmd = cmd_line[2]
            if cmd == "enable":
                bc.config.plugins[plugin_name]["autostart"] = True
                await Command.send_message(execution_ctx, f"Autostart for plugin '{plugin_name}' has been enabled")
            elif cmd == "disable":
                bc.config.plugins[plugin_name]["autostart"] = False
                await Command.send_message(execution_ctx, f"Autostart for plugin '{plugin_name}' has been disabled")
            else:
                await Command.send_message(
                    execution_ctx, f"Unknown subcommand '{cmd}' for plugin autostart manipulation")
