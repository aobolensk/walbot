from src import const
from src.commands import BaseCmd
from src.config import bc
from src.embed import DiscordEmbed
from src.message import Msg
from src.utils import Util


class PluginCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "listplugin",
                                     permission=const.Permission.USER.value, subcommand=False)

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
