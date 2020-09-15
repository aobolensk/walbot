from .. import const
from ..commands import BaseCmd
from ..config import Reaction
from ..config import Response
from ..config import bc
from ..utils import Util


class ReactionCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "addreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "updreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delreaction",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listreaction",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "addresponse",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "updresponse",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "delresponse",
                                     permission=const.Permission.MOD.value, subcommand=False)
        bc.commands.register_command(__name__, self.get_classname(), "listresponse",
                                     permission=const.Permission.USER.value, subcommand=True)

    @staticmethod
    async def _addreaction(message, command, silent=False):
        """Add reaction
    Example: !addreaction emoji regex"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        bc.config.reactions[bc.config.ids["reaction"]] = Reaction(' '.join(command[2:]), command[1])
        bc.config.ids["reaction"] += 1
        await Util.response(message, f"Reaction '{command[1]}' on '{' '.join(command[2:])}' successfully added", silent)

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
            await Util.response(
                message, f"Reaction '{command[1]}' on '{' '.join(command[2:])}' successfully updated", silent)
        else:
            await Util.response(message, "Incorrect index of reaction!", silent)

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
            await Util.response(message, "Successfully deleted reaction!", silent)
        else:
            await Util.response(message, "Invalid index of reaction!", silent)

    @staticmethod
    async def _listreaction(message, command, silent=False):
        """Print list of reactions
    Example: !listreaction"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, reaction in bc.config.reactions.items():
            result += f"{index} - {reaction.emoji}: `{reaction.regex}`\n"
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No reactions found!", silent)
        return result

    @staticmethod
    async def _addresponse(message, command, silent=False):
        """Add bot response on message that contains particular regex
    Example: !addresponse regex;text"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        parts = ' '.join(command[1:]).split(';', 1)
        if len(parts) < 2:
            await Util.response(
                message, "You need to provide regex and text that are separated by semicolon (;)", silent)
            return
        regex, text = parts
        bc.config.responses[bc.config.ids["response"]] = Response(regex, text)
        bc.config.ids["response"] += 1
        await Util.response(message, f"Response '{text}' on '{regex}' successfully added", silent)

    @staticmethod
    async def _updresponse(message, command, silent=False):
        """Update bot response
    Example: !updresponse index regex;text"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should an index (integer)", silent)
        if index is None:
            return
        if index in bc.config.responses.keys():
            parts = ' '.join(command[2:]).split(';', 1)
            if len(parts) < 2:
                await Util.response(
                    message, "You need to provide regex and text that are separated by semicolon (;)", silent)
                return
            regex, text = parts
            bc.config.responses[index] = Response(regex, text)
            await Util.response(message, f"Response '{text}' on '{regex}' successfully updated", silent)
        else:
            await Util.response(message, "Incorrect index of response!", silent)

    @staticmethod
    async def _delresponse(message, command, silent=False):
        """Delete response
    Examples:
        !delresponse index"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int(
            message, command[1], f"Second parameter for '{command[0]}' should be an index of response", silent)
        if index is None:
            return
        if index in bc.config.responses.keys():
            bc.config.responses.pop(index)
            await Util.response(message, "Successfully deleted response!", silent)
        else:
            await Util.response(message, "Invalid index of response!", silent)

    @staticmethod
    async def _listresponse(message, command, silent=False):
        """Print list of responses
    Example: !listresponse"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        for index, response in bc.config.responses.items():
            result += f"{index} - `{response.regex}`: {response.text}\n"
        if result:
            await Util.response(message, result, silent)
        else:
            await Util.response(message, "No responses found!", silent)
        return result
