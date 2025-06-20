import uuid
from typing import List

from src import const
from src.api.command import (
    BaseCmd,
    Command,
    Implementation,
    SupportedPlatforms
)
from src.api.execution_context import ExecutionContext
from src.config import User, bc
from src.log import log


class AuthCommands(BaseCmd):
    def bind(self) -> None:
        bc.executor.commands["authorize"] = Command(
            "auth", "authorize", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._authorize,
            supported_platforms=SupportedPlatforms.TELEGRAM)
        bc.executor.commands["resetpass"] = Command(
            "auth", "resetpass", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._resetpass,
            supported_platforms=SupportedPlatforms.TELEGRAM)

    async def _authorize(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Authorize Telegram backend for current channel
        Run this command and give passphrase from config.yaml as an argument
    Example: !authorize <passphrase>"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2, max=2):
            return
        if execution_ctx.update.message.from_user.id not in bc.config.telegram.users.keys():
            bc.config.telegram.users[execution_ctx.update.message.from_user.id] = User(
                execution_ctx.update.message.from_user.id)
        passphrase = execution_ctx.context.args[0] if execution_ctx.context.args else ""
        if passphrase == bc.config.telegram.passphrase:
            bc.config.telegram.channel_whitelist.add(execution_ctx.update.effective_chat.id)
            await Command.send_message(execution_ctx, "Channel has been added to whitelist")
        else:
            await Command.send_message(execution_ctx, "Wrong passphrase!")

    async def _resetpass(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Reset passphrase for Telegram backend authorization, set it to config.yaml and dump to walbot log
    Example: !resetpass"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        bc.config.telegram.passphrase = uuid.uuid4().hex
        log.warning("Passphrase has been changed. New passphrase: " + bc.config.telegram.passphrase)
        await Command.send_message(execution_ctx, 'Passphrase has been reset!')
