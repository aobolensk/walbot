"""Role commands"""

from typing import List

import discord

from src import const
from src.api.command import (
    BaseCmd,
    Command,
    Implementation,
    SupportedPlatforms
)
from src.api.execution_context import ExecutionContext
from src.config import bc


class RoleCommands(BaseCmd):
    def bind(self):
        bc.executor.commands["addrole"] = Command(
            "role", "addrole", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._addrole,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["listrole"] = Command(
            "role", "listrole", const.Permission.USER, Implementation.FUNCTION,
            subcommand=False, impl_func=self._listrole,
            supported_platforms=SupportedPlatforms.DISCORD)
        bc.executor.commands["delrole"] = Command(
            "role", "delrole", const.Permission.MOD, Implementation.FUNCTION,
            subcommand=False, impl_func=self._delrole,
            supported_platforms=SupportedPlatforms.DISCORD)

    async def _addrole(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Assign a role to the user
    Usage: !addrole @user role_name"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        user = cmd_line[1]
        role_name = ' '.join(cmd_line[2:])
        role = discord.utils.get(execution_ctx.message.guild.roles, name=role_name)
        if role is None:
            return await Command.send_message(execution_ctx, f"Role '{role_name}' does not exist")
        if not execution_ctx.message.mentions:
            return await Command.send_message(execution_ctx, "You must mention a user to assign role")
        member = await execution_ctx.message.guild.fetch_member(execution_ctx.message.mentions[0].id)
        if member is None:
            return await Command.send_message(execution_ctx, f"User '{user}' does not exist")
        try:
            await member.add_roles(role)
        except discord.HTTPException as e:
            return await Command.send_message(
                execution_ctx, f"Role '{role_name}' could not be assigned to user '{user}'. ERROR: '{e}'")
        await Command.send_message(execution_ctx, f"Successfully assigned role '{role_name}' to user '{user}'")

    async def _listrole(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Print list of all roles available on this server
    Usage: !listrole"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=1, max=1):
            return
        roles = await execution_ctx.message.guild.fetch_roles()
        result = '\n'.join(sorted((role.name for role in roles)))
        if result:
            result = await execution_ctx.disable_pings(result)
            await Command.send_message(execution_ctx, result)
        else:
            await Command.send_message(execution_ctx, "No roles available")

    async def _delrole(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        """Unassign a role from the user
    Usage: !delrole @user role_name"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return
        user = cmd_line[1]
        role_name = ' '.join(cmd_line[2:])
        role = discord.utils.get(execution_ctx.message.guild.roles, name=role_name)
        if role is None:
            return await Command.send_message(execution_ctx, f"Role '{role_name}' does not exist")
        if not execution_ctx.message.mentions:
            return await Command.send_message(execution_ctx, "You must mention a user to delete role")
        member = await execution_ctx.message.guild.fetch_member(execution_ctx.message.mentions[0].id)
        if member is None:
            return await Command.send_message(execution_ctx, f"User '{user}' does not exist")
        try:
            await member.remove_roles(role)
        except discord.HTTPException as e:
            return await Command.send_message(
                execution_ctx, f"Role '{role_name}' could not be deleted from user '{user}'. ERROR: '{e}'")
        await Command.send_message(execution_ctx, f"Successfully deleted role '{role_name}' from user '{user}'")
