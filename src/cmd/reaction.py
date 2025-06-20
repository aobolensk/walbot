from typing import List, Optional

from src import const
from src.api.command import (
    BaseCmd,
    Command,
    Implementation,
    SupportedPlatforms
)
from src.api.execution_context import ExecutionContext
from src.config import Reaction, Response, bc
from src.utils import Util


class ReactionCommands(BaseCmd):
    def bind(self) -> None:
        bc.executor.commands["addreaction"] = Command(
            "reaction", "addreaction", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addreaction,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["updreaction"] = Command(
            "reaction", "updreaction", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._updreaction,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["delreaction"] = Command(
            "reaction", "delreaction", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delreaction,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["listreaction"] = Command(
            "reaction", "listreaction", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._listreaction,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["addresponse"] = Command(
            "reaction", "addresponse", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addresponse,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["updresponse"] = Command(
            "reaction", "updresponse", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._updresponse,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["delresponse"] = Command(
            "reaction", "delresponse", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delresponse,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))
        bc.executor.commands["listresponse"] = Command(
            "reaction", "listresponse", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listresponse,
            supported_platforms=(SupportedPlatforms.DISCORD | SupportedPlatforms.TELEGRAM))

    async def _addreaction(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add reaction
    Example: !addreaction emoji regex"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return None
        bc.config.reactions[bc.config.ids["reaction"]] = Reaction(' '.join(cmd_line[2:]), cmd_line[1])
        bc.config.ids["reaction"] += 1
        await Command.send_message(
            execution_ctx, f"Reaction '{cmd_line[1]}' on '{' '.join(cmd_line[2:])}' successfully added")

    async def _updreaction(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Update reaction
    Example: !updreaction index emoji regex"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=4):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should an index (integer)")
        if index is None:
            return
        if index in bc.config.reactions.keys():
            bc.config.reactions[index] = Reaction(' '.join(cmd_line[3:]), cmd_line[2])
            await Command.send_message(
                execution_ctx, f"Reaction '{cmd_line[1]}' on '{' '.join(cmd_line[2:])}' successfully updated")
        else:
            await Command.send_message(execution_ctx, "Incorrect index of reaction!")

    async def _delreaction(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete reaction
    Examples:
        !delreaction index"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of reaction")
        if index is None:
            return
        if index in bc.config.reactions.keys():
            bc.config.reactions.pop(index)
            await Command.send_message(execution_ctx, "Successfully deleted reaction!")
        else:
            await Command.send_message(execution_ctx, "Invalid index of reaction!")

    async def _listreaction(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Print list of reactions
    Example: !listreaction"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = ""
        for index, reaction in bc.config.reactions.items():
            result += f"{index} - {reaction.emoji}: `{reaction.regex}`\n"
        await Command.send_message(execution_ctx, result or "No reactions found!")
        return result

    async def _addresponse(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add bot response on message that contains particular regex
    Example: !addresponse regex;text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        parts = ' '.join(cmd_line[1:]).split(';', 1)
        if len(parts) < 2:
            return await Command.send_message(
                execution_ctx, "You need to provide regex and text that are separated by semicolon (;)")
        regex, text = parts
        bc.config.responses[bc.config.ids["response"]] = Response(regex, text)
        bc.config.ids["response"] += 1
        await Command.send_message(execution_ctx, f"Response '{text}' on '{regex}' successfully added")

    async def _updresponse(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Update bot response
    Example: !updresponse index regex;text"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should an index (integer)")
        if index is None:
            return
        if index not in bc.config.responses.keys():
            return await Command.send_message(execution_ctx, "Incorrect index of response!")
        parts = ' '.join(cmd_line[2:]).split(';', 1)
        if len(parts) < 2:
            return await Command.send_message(
                execution_ctx, "You need to provide regex and text that are separated by semicolon (;)")
        regex, text = parts
        bc.config.responses[index] = Response(regex, text)
        await Command.send_message(execution_ctx, f"Response '{text}' on '{regex}' successfully updated")

    async def _delresponse(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete response
    Examples:
        !delresponse index"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return None
        index = await Util.parse_int(
            execution_ctx, cmd_line[1], f"Second parameter for '{cmd_line[0]}' should be an index of response")
        if index is None:
            return
        if index not in bc.config.responses.keys():
            return await Command.send_message(execution_ctx, "Invalid index of response!")
        bc.config.responses.pop(index)
        await Command.send_message(execution_ctx, "Successfully deleted response!")

    async def _listresponse(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Print list of responses
    Example: !listresponse"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return None
        result = ""
        for index, response in bc.config.responses.items():
            result += f"{index} - `{response.regex}`: {response.text}\n"
        await Command.send_message(execution_ctx, result or "No responses found!")
        return result
