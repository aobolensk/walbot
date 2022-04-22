"""Markov model commands"""

import discord

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.utils import Util, null


class RoleCommands(BaseCmd):
    def bind(self):
        bc.commands.register_commands(__name__, self.get_classname(), {
            "addrole": dict(permission=const.Permission.MOD.value, subcommand=False),
            "listrole": dict(permission=const.Permission.USER.value, subcommand=False),
            "delrole": dict(permission=const.Permission.MOD.value, subcommand=False),
        })

    @staticmethod
    async def _addrole(message, command, silent=False):
        """Assign a role to the user
    Usage: !addrole @user role_name"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        user = command[1]
        role_name = ' '.join(command[2:])
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role is None:
            return null(await Msg.response(message, f"Role '{role_name}' does not exist", silent))
        member = await message.guild.fetch_member(message.mentions[0].id)
        if member is None:
            return null(await Msg.response(message, f"User '{user}' does not exist", silent))
        try:
            await member.add_roles(role)
        except discord.HTTPException as e:
            return await null(
                Msg.response(
                    message, f"Role '{role_name}' could not be assigned to user '{user}'. ERROR: '{e}'", silent))
        await Msg.response(message, f"Successfully assigned role '{role_name}' to user '{user}'", silent)

    @staticmethod
    async def _listrole(message, command, silent=False):
        """Print list of all roles available on this server
    Usage: !listrole"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        roles = await message.guild.fetch_roles()
        result = ""
        for role in roles:
            result += f"{role.name}\n"
        if result:
            await Msg.response(message, await bc.config.disable_pings_in_response(message, result, force=True), silent)
        else:
            await Msg.response(message, "No roles available", silent)

    @staticmethod
    async def _delrole(message, command, silent=False):
        """Unassign a role from the user
    Usage: !delrole @user role_name"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        user = command[1]
        role_name = ' '.join(command[2:])
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role is None:
            return null(await Msg.response(message, f"Role '{role_name}' does not exist", silent))
        member = await message.guild.fetch_member(message.mentions[0].id)
        if member is None:
            return null(await Msg.response(message, f"User '{user}' does not exist", silent))
        try:
            await member.remove_roles(role)
        except discord.HTTPException as e:
            return await null(
                Msg.response(
                    message, f"Role '{role_name}' could not be assigned to user '{user}'. ERROR: '{e}'", silent))
        await Msg.response(message, f"Successfully assigned role '{role_name}' to user '{user}'", silent)
