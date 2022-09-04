"""Management of bot reactions to user messages"""

from src import const
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import Reaction, bc
from src.utils import Util


class ReactionCommands(BaseCmd):
    def bind(self):
        bc.discord.commands.register_commands(__name__, self.get_classname(), {
            "addreaction": dict(permission=const.Permission.MOD.value, subcommand=False),
            "updreaction": dict(permission=const.Permission.MOD.value, subcommand=False),
            "delreaction": dict(permission=const.Permission.MOD.value, subcommand=False),
            "listreaction": dict(permission=const.Permission.USER.value, subcommand=True),
        })

    @staticmethod
    async def _addreaction(message, command, silent=False):
        """Add reaction
    Example: !addreaction emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        bc.config.reactions[bc.config.ids["reaction"]] = Reaction(' '.join(command[2:]), command[1])
        bc.config.ids["reaction"] += 1
        await Msg.response(message, f"Reaction '{command[1]}' on '{' '.join(command[2:])}' successfully added", silent)

    @staticmethod
    async def _updreaction(message, command, silent=False):
        """Update reaction
    Example: !updreaction index emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=4):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should an index (integer)", silent)
        if index is None:
            return
        if index in bc.config.reactions.keys():
            bc.config.reactions[index] = Reaction(' '.join(command[3:]), command[2])
            await Msg.response(
                message, f"Reaction '{command[1]}' on '{' '.join(command[2:])}' successfully updated", silent)
        else:
            await Msg.response(message, "Incorrect index of reaction!", silent)

    @staticmethod
    async def _delreaction(message, command, silent=False):
        """Delete reaction
    Examples:
        !delreaction index"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of reaction", silent)
        if index is None:
            return
        if index in bc.config.reactions.keys():
            bc.config.reactions.pop(index)
            await Msg.response(message, "Successfully deleted reaction!", silent)
        else:
            await Msg.response(message, "Invalid index of reaction!", silent)

    @staticmethod
    async def _listreaction(message, command, silent=False):
        """Print list of reactions
    Example: !listreaction"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, reaction in bc.config.reactions.items():
            result += f"{index} - {reaction.emoji}: `{reaction.regex}`\n"
        await Msg.response(message, result or "No reactions found!", silent)
        return result
