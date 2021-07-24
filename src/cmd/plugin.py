from src import const
from src.commands import BaseCmd
from src.config import bc
from src.embed import DiscordEmbed
from src.message import Msg
from src.utils import Util, null


class PluginCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "listplugin",
                                     permission=const.Permission.USER.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "loadplugin",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "unloadplugin",
                                     permission=const.Permission.MOD.value, subcommand=False)

    @staticmethod
    async def _listplugin(message, command, silent=False):
        """Print list of plugins
    Usage:
        !listplugin"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        plugin_names = bc.plugin_manager.get_plugins_list()
        e = DiscordEmbed()
        e.title("List of plugins")
        for plugin_name in plugin_names:
            is_enabled = bc.plugin_manager.get_plugin(plugin_name)
            e.add_field(plugin_name, "enabled" if is_enabled else "disabled", True)
        await Msg.response(message, None, silent, embed=e.get())

    @staticmethod
    async def _loadplugin(message, command, silent=False):
        """Load plugin by its name
    Usage:
        !loadplugin <plugin_name>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        plugin_name = command[1]
        plugin = bc.plugin_manager.get_plugin(plugin_name)
        if plugin is None:
            return null(await Msg.response(message, f"Could not find plugin '{plugin_name}'", silent))
        await plugin.init()
        await Msg.response(message, f"Plugin '{plugin_name}' has been loaded", silent)

    @staticmethod
    async def _unloadplugin(message, command, silent=False):
        """Unload plugin by its name
    Usage:
        !unloadplugin <plugin_name>"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        plugin_name = command[1]
        plugin = bc.plugin_manager.get_plugin(plugin_name)
        if plugin is None:
            return null(await Msg.response(message, f"Could not find plugin '{plugin_name}'", silent))
        await plugin.close()
        await Msg.response(message, f"Plugin '{plugin_name}' has been unloaded", silent)
