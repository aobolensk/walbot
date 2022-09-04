from typing import List

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.backend.telegram.cmd.common import CommonCommands
from src.config import Command as LegacyDiscordCommand
from src.config import bc


class CustomCmdsCommands(BaseCmd):
    def __init__(self) -> None:
        pass

    def bind(self) -> None:
        bc.executor.commands["addextcmd"] = Command(
            "custom-commands", "addextcmd", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addextcmd, postpone_execution=True)
        bc.executor.commands["updextcmd"] = Command(
            "custom-commands", "updextcmd", const.Permission.ADMIN, Implementation.FUNCTION,
            subcommand=False, impl_func=self._updextcmd, postpone_execution=True)
        bc.executor.commands["delcmd"] = Command(
            "custom-commands", "delcmd", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delcmd)

    async def _addextcmd(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Add command that executes external process
    Note: Be careful when you are executing external commands!
    Example: !addextcmd uname uname -a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        command_name = cmd_line[1]
        if command_name in bc.executor.commands.keys():
            return await Command.send_message(execution_ctx, f"Command {command_name} already exists")
        if command_name in bc.discord.commands.data.keys():
            return await Command.send_message(
                execution_ctx, f"Command {command_name} already exists (on Discord backend)")
        external_cmd_line = ' '.join(cmd_line[2:])
        bc.executor.commands[cmd_line[1]] = Command(
            None, command_name, const.Permission.ADMIN, Implementation.EXTERNAL_CMDLINE,
            subcommand=True, impl_message=external_cmd_line)
        bc.discord.commands.data[command_name] = LegacyDiscordCommand(
            command_name, cmd_line=external_cmd_line)
        if execution_ctx.platform == "discord":
            bc.discord.commands.data[command_name].channels.append(execution_ctx.message.channel.id)
        if bc.backends["telegram"]:
            CommonCommands.add_handler(bc.telegram.dispatcher, bc.executor.commands[cmd_line[1]])
        await Command.send_message(
            execution_ctx,
            f"Command '{command_name}' that calls external command `{external_cmd_line}` is successfully added")

    async def _updextcmd(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Update command that executes external process (works only for commands that already exist)
    Note: Be careful when you are executing external commands!
    Example: !updextcmd uname uname -a"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        command_name = cmd_line[1]
        if command_name not in bc.executor.commands.keys():
            return await Command.send_message(execution_ctx, f"Command '{command_name}' does not exist")
        if (bc.executor.commands[command_name].impl_type != Implementation.EXTERNAL_CMDLINE or
                bc.executor.commands[command_name].impl_message is None):
            return await Command.send_message(execution_ctx, f"Command '{command_name}' is not editable")
        external_cmd_line = ' '.join(cmd_line[2:])
        bc.executor.commands[command_name].impl_message = external_cmd_line
        return await Command.send_message(
            execution_ctx,
            f"Command '{command_name}' that calls external command `{external_cmd_line}` is successfully updated")

    async def _delcmd(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Delete command
    Example: !delcmd hello"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        command_name = cmd_line[1]
        if command_name not in bc.executor.commands.keys():
            await Command.send_message(
                execution_ctx, f"WARN: Command '{command_name}' does not exist (in common commands)")
        if command_name not in bc.discord.commands.data.keys():
            await Command.send_message(
                execution_ctx, f"WARN: Command '{command_name}' does not exist (on Discord backend")
        bc.executor.commands.pop(command_name, None)
        bc.discord.commands.data.pop(command_name, None)
        if bc.backends["telegram"] and command_name in bc.telegram.handlers.keys():
            CommonCommands.remove_handler(bc.telegram.dispatcher, command_name)
        return await Command.send_message(execution_ctx, f"Command '{command_name}' successfully deleted")
