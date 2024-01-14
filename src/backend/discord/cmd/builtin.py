"""Built-in WalBot commands"""

import math
import os
import tempfile
import urllib.parse
import urllib.request

import discord

from src import const
from src.algorithms import levenshtein_distance
from src.api.command import BaseCmd
from src.backend.discord.message import Msg
from src.config import Command, bc, log
from src.utils import Util, null


class BuiltinCommands(BaseCmd):
    def bind(self):
        bc.discord.commands.register_commands(__name__, self.get_classname(), {
            "help": dict(permission=const.Permission.USER.value, subcommand=False),
            "addcmd": dict(permission=const.Permission.MOD.value, subcommand=False),
            "updcmd": dict(permission=const.Permission.MOD.value, subcommand=False),
            "enablecmd": dict(permission=const.Permission.MOD.value, subcommand=False),
            "disablecmd": dict(permission=const.Permission.MOD.value, subcommand=False),
            "permcmd": dict(permission=const.Permission.ADMIN.value, subcommand=False),
            "timescmd": dict(permission=const.Permission.USER.value, subcommand=True),
            "setmaxexeccmdtime": dict(permission=const.Permission.MOD.value, subcommand=False),
            "permuser": dict(permission=const.Permission.ADMIN.value, subcommand=False),
            "whitelist": dict(permission=const.Permission.MOD.value, subcommand=False),
            "config": dict(permission=const.Permission.MOD.value, subcommand=False),
            "silent": dict(permission=const.Permission.USER.value, subcommand=False),
            "addalias": dict(permission=const.Permission.MOD.value, subcommand=False),
            "delalias": dict(permission=const.Permission.MOD.value, subcommand=False),
            "listalias": dict(permission=const.Permission.USER.value, subcommand=True),
            "avatar": dict(permission=const.Permission.MOD.value, subcommand=False),
            "pin": dict(permission=const.Permission.MOD.value, subcommand=True),
            "slowmode": dict(permission=const.Permission.MOD.value, subcommand=False),
            "permlevel": dict(permission=const.Permission.USER.value, subcommand=False),
            "disabletl": dict(permission=const.Permission.MOD.value, subcommand=False, max_execution_time=-1),
        })

    @staticmethod
    async def _help(message, command, silent=False):
        """Print list of commands and get examples
    Examples:
        !help
        !help -p
        !help help"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        if len(command) == 1 or (len(command) == 2 and command[1] == '-p'):
            commands = []
            for name, cmd in bc.discord.commands.data.items():
                if cmd.message is not None:
                    s = (name, cmd.message)
                    commands.append(s)
                elif cmd.cmd_line is not None:
                    s = (name, f"calls external command `{cmd.cmd_line}`")
                    commands.append(s)
                elif cmd.is_private:
                    s = (name, "*Private command*\n" + (cmd.get_actor().__doc__ or "*<No docs provided>*"))
                    commands.append(s)
            commands.sort()
            version = bc.info.version
            if len(command) == 2 and command[1] == '-p':
                # Plain text help
                result = (f"Built-in commands <{const.GIT_REPO_LINK}/blob/" +
                          (version if version != ' ' else "master") + "/" + const.DISCORD_COMMANDS_DOC_PATH + ">\n")
                for cmd in commands:
                    result += f"**{cmd[0]}**: {cmd[1]}\n"
                await Msg.response(message, result, silent, suppress_embeds=True)
            else:
                # Embed help
                commands.insert(
                    0, ("Built-in commands", (
                        f"<{const.GIT_REPO_LINK}/blob/" +
                        (version if version != ' ' else "master") + "/" + const.DISCORD_COMMANDS_DOC_PATH + ">")))
                cur_list = 1
                total_list = int(math.ceil(len(commands) / const.DISCORD_MAX_EMBED_FILEDS_COUNT))
                for chunk in Msg.split_by_chunks(commands, const.DISCORD_MAX_EMBED_FILEDS_COUNT):
                    title = "Help"
                    if total_list > 1:
                        title += f" ({cur_list}/{total_list})"
                    cur_list += 1
                    embed = discord.Embed(title=title, color=0x717171)
                    for cmd in chunk:
                        cmd_name = cmd[0]
                        description = cmd[1]
                        description = Util.cut_string(description, 1024)
                        embed.add_field(name=cmd_name, value=description, inline=False)
                    await Msg.response(message, None, silent, embed=embed)
        elif len(command) == 2:
            name = command[1]
            if command[1] in bc.discord.commands.data:
                command = bc.discord.commands.data[command[1]]
            elif command[1] in bc.discord.commands.aliases.keys():
                command = bc.discord.commands.data[bc.discord.commands.aliases[command[1]]]
            else:
                return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
            result = name + ": "
            if command.perform is not None:
                if (command.get_actor().__doc__ is not None and
                        "new function with partial application" not in command.get_actor().__doc__):
                    result += command.get_actor().__doc__.strip()
                elif name in bc.executor.commands.keys():
                    result += bc.executor.commands[name].description.strip()
                else:
                    result += "*<No docs provided>*"
            elif command.message is not None:
                result += "`" + command.message + "`"
            elif command.cmd_line is not None:
                result += f"calls external command `{command.cmd_line}`"
            else:
                result += "<error>"
            result += '\n'
            result += f"    Required permission level: {command.permission}\n"
            if command.subcommand:
                result += "    This command can be used as subcommand\n"
            await Msg.response(message, result, silent)

    @staticmethod
    async def _addcmd(message, command, silent=False):
        """Add command
    Example: !addcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.discord.commands.data.keys():
            return null(await Msg.response(message, f"Command {command_name} already exists", silent))
        bc.discord.commands.data[command_name] = Command(command_name, message=' '.join(command[2:]))
        bc.discord.commands.data[command_name].channels.append(message.channel.id)
        await Msg.response(
            message,
            f"Command '{command_name}' -> '{bc.discord.commands.data[command_name].message}' successfully added",
            silent)

    @staticmethod
    async def _updcmd(message, command, silent=False):
        """Update command (works only for commands that already exist)
    Example: !updcmd hello Hello!"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        command_name = command[1]
        if command_name in bc.discord.commands.data.keys():
            if bc.discord.commands.data[command_name].message is None:
                return null(await Msg.response(message, f"Command '{command_name}' is not editable", silent))
            bc.discord.commands.data[command_name].message = ' '.join(command[2:])
            return null(
                await Msg.response(
                    message, f"Command '{command_name}' -> "
                             f"'{bc.discord.commands.data[command_name].message}' successfully updated", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _enablecmd(message, command, silent=False):
        """Enable command in specified scope
    Examples:
        !enablecmd ping
        !enablecmd ping channel
        !enablecmd ping guild
        !enablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        command_name = command[1]
        if command_name in bc.discord.commands.data.keys():
            if len(command) == 2 or command[2] == "channel":
                if message.channel.id not in bc.discord.commands.data[command_name].channels:
                    bc.discord.commands.data[command_name].channels.append(message.channel.id)
                await Msg.response(message, f"Command '{command_name}' is enabled in this channel", silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id not in bc.discord.commands.data[command_name].channels:
                        bc.discord.commands.data[command_name].channels.append(channel.id)
                await Msg.response(message, f"Command '{command_name}' is enabled in this guild", silent)
            elif command[2] == "global":
                bc.discord.commands.data[command_name].is_global = True
                await Msg.response(message, f"Command '{command_name}' is enabled in global scope", silent)
            else:
                await Msg.response(message, f"Unknown scope '{command[2]}'", silent)
            return
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _disablecmd(message, command, silent=False):
        """Disable command in specified scope
    Examples:
        !disablecmd ping
        !disablecmd ping channel
        !disablecmd ping guild
        !disablecmd ping global"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        command_name = command[1]
        if command_name in bc.discord.commands.data.keys():
            if len(command) == 2 or command[2] == "channel":
                if message.channel.id in bc.discord.commands.data[command_name].channels:
                    bc.discord.commands.data[command_name].channels.remove(message.channel.id)
                await Msg.response(message, f"Command '{command_name}' is disabled in this channel", silent)
            elif command[2] == "guild":
                for channel in message.channel.guild.text_channels:
                    if channel.id in bc.discord.commands.data[command_name].channels:
                        bc.discord.commands.data[command_name].channels.remove(channel.id)
                await Msg.response(message, f"Command '{command_name}' is disabled in this guild", silent)
            elif command[2] == "global":
                bc.discord.commands.data[command_name].is_global = False
                await Msg.response(message, f"Command '{command_name}' is disabled in global scope", silent)
            else:
                await Msg.response(message, f"Unknown scope '{command[2]}'", silent)
            return
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _permcmd(message, command, silent=False):
        """Set commands permission
    Example: !permcmd ping 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        command_name = command[1]
        perm = await Util.parse_int_for_discord(
            message, command[2], f"Third argument of command '{command[0]}' should be an integer", silent)
        if perm is None:
            return
        if command_name in bc.discord.commands.data.keys():
            bc.discord.commands.data[command_name].permission = perm
            return null(
                await Msg.response(
                    message, f"Set permission level {command[2]} for command '{command_name}'", silent))
        await Msg.response(message, f"Command '{command_name}' does not exist", silent)

    @staticmethod
    async def _timescmd(message, command, silent=False):
        """Print how many times command was invoked
    Examples:
        !timescmd echo
        !timescmd echo -s"""
        if not await Util.check_args_count(message, command, silent, min=2, max=3):
            return
        if command[1] in bc.config.commands.aliases.keys():
            command[1] = bc.config.commands.aliases[command[1]]
        if command[1] not in bc.discord.commands.data.keys():
            return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
        com = bc.discord.commands.data[command[1]]
        times = com.times_called
        if len(command) == 3 and command[2] == '-s':
            result = f"{times}"
        else:
            result = f"Command '{command[1]}' was invoked {times} times"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _setmaxexeccmdtime(message, command, silent=False):
        """Print how many times command was invoked
    Example: !setmaxexeccmdtime echo 3"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        if command[1] in bc.config.commands.aliases.keys():
            command[1] = bc.config.commands.aliases[command[1]]
        if command[1] not in bc.discord.commands.data.keys():
            return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
        com = bc.discord.commands.data[command[1]]
        max_exec_time = await Util.parse_int_for_discord(
            message, command[2], f"Third argument of command '{command[0]}' should be an integer", silent)
        com.max_execution_time = max_exec_time
        await Msg.response(
            message, f"Set maximal execution time for command '{command[1]}' to {max_exec_time}", silent)

    @staticmethod
    async def _permuser(message, command, silent=False):
        """Set user permission
    Example: !permuser @nickname 0"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        perm = await Util.parse_int_for_discord(
            message, command[2], f"Third argument of command '{command[0]}' should be an integer", silent)
        if perm is None:
            return
        r = const.DISCORD_USER_ID_REGEX.search(command[1])
        if r is None:
            return null(
                await Msg.response(
                    message, f"Second argument of command '{command[0]}' should be user ping", silent))
        user_id = int(r.group(1))
        if user_id in bc.config.discord.users.keys():
            bc.config.discord.users[user_id].permission_level = perm
            return null(
                await Msg.response(message, f"Set permission level {command[2]} for user '{command[1]}'", silent))
        else:
            return null(
                await Msg.response(message, f"User '{command[1]}' is not found", silent))

    @staticmethod
    async def _whitelist(message, command, silent=False):
        """Bot's whitelist
    Examples:
        !whitelist enable/disable
        !whitelist add
        !whitelist remove"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] == "enable":
            bc.config.discord.guilds[message.channel.guild.id].is_whitelisted = True
            await Msg.response(message, "This guild is whitelisted for bot", silent)
        elif command[1] == "disable":
            bc.config.discord.guilds[message.channel.guild.id].is_whitelisted = False
            await Msg.response(message, "This guild is not whitelisted for bot", silent)
        elif command[1] == "add":
            bc.config.discord.guilds[message.channel.guild.id].whitelist.add(message.channel.id)
            await Msg.response(message, "This channel is added to bot's whitelist", silent)
        elif command[1] == "remove":
            bc.config.discord.guilds[message.channel.guild.id].whitelist.discard(message.channel.id)
            await Msg.response(message, "This channel is removed from bot's whitelist", silent)
        else:
            await Msg.response(message, f"Unknown argument '{command[1]}'", silent)

    async def __config_view(message, silent=False):
        header = f"Config for channel {message.channel}:"

        class ConfigView(discord.ui.View):
            def __init__(self, timeout=60, disable_on_timeout=True):
                super().__init__(timeout=timeout)
                self.disable_on_timeout = disable_on_timeout

            @discord.ui.button(
                label="Bot reactions",
                style=(
                    discord.ButtonStyle.green
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist
                    else discord.ButtonStyle.red
                ))
            async def bot_reactions_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if (bc.config.discord.users[interaction.user.id].permission_level <
                        bc.config.commands.data["config2"].permission):
                    await Msg.response(
                        message, f"{interaction.user.mention} you don't have permission to use this command", silent)
                    return
                if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist:
                    bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist.remove(message.channel.id)
                    button.style = discord.ButtonStyle.red
                else:
                    bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                    button.style = discord.ButtonStyle.green
                await interaction.response.edit_message(content=header, view=self)
                await Msg.response(
                    message,
                    f"{message.author.mention} Bot reactions are " + (
                        "enabled"
                        if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist
                        else "disabled"), silent)

            @discord.ui.button(
                label="Markov logging",
                style=(
                    discord.ButtonStyle.green
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist
                    else discord.ButtonStyle.red
                ))
            async def markov_logging_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if (bc.config.discord.users[interaction.user.id].permission_level <
                        bc.config.commands.data["config2"].permission):
                    await Msg.response(
                        message, f"{interaction.user.mention} you don't have permission to use this command", silent)
                    return
                if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist:
                    bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist.remove(
                        message.channel.id)
                    button.style = discord.ButtonStyle.red
                else:
                    bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist.add(message.channel.id)
                    button.style = discord.ButtonStyle.green
                await interaction.response.edit_message(content=header, view=self)
                await Msg.response(
                    message,
                    f"{message.author.mention} Markov logging is " + (
                        "enabled"
                        if message.channel.id
                        in bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist
                        else "disabled"), silent)

            @discord.ui.button(
                label="Bot responses",
                style=(
                    discord.ButtonStyle.green
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].responses_whitelist
                    else discord.ButtonStyle.red
                ))
            async def bot_responses_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if (bc.config.discord.users[interaction.user.id].permission_level <
                        bc.config.commands.data["config2"].permission):
                    await Msg.response(
                        message, f"{interaction.user.mention} you don't have permission to use this command", silent)
                    return
                if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].responses_whitelist:
                    bc.config.discord.guilds[message.channel.guild.id].responses_whitelist.remove(message.channel.id)
                    button.style = discord.ButtonStyle.red
                else:
                    bc.config.discord.guilds[message.channel.guild.id].responses_whitelist.add(message.channel.id)
                    button.style = discord.ButtonStyle.green
                await interaction.response.edit_message(content=header, view=self)
                await Msg.response(
                    message,
                    f"{message.author.mention} Bot responses are " + (
                        "enabled"
                        if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].responses_whitelist
                        else "disabled"), silent)

            @discord.ui.button(
                label="Markov responses",
                style=(
                    discord.ButtonStyle.green
                    if message.channel.id
                    in bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist
                    else discord.ButtonStyle.red
                ))
            async def markov_reactions_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if (bc.config.discord.users[interaction.user.id].permission_level <
                        bc.config.commands.data["config2"].permission):
                    await Msg.response(
                        message, f"{interaction.user.mention} you don't have permission to use this command", silent)
                    return
                if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist:
                    bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist.remove(
                        message.channel.id)
                    button.style = discord.ButtonStyle.red
                else:
                    bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist.add(
                        message.channel.id)
                    button.style = discord.ButtonStyle.green
                await interaction.response.edit_message(content=header, view=self)
                await Msg.response(
                    message,
                    f"{message.author.mention} Markov responses are " + (
                        "enabled"
                        if message.channel.id
                        in bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist
                        else "disabled"), silent)

            @discord.ui.button(
                label="Markov pings",
                style=(
                    discord.ButtonStyle.green
                    if bc.config.discord.guilds[message.channel.guild.id].markov_pings
                    else discord.ButtonStyle.red
                ))
            async def markov_pings_button(self, button: discord.ui.Button, interaction: discord.Interaction):
                if (bc.config.discord.users[interaction.user.id].permission_level <
                        bc.config.commands.data["config2"].permission):
                    await Msg.response(
                        message, f"{interaction.user.mention} you don't have permission to use this command", silent)
                    return
                if bc.config.discord.guilds[message.channel.guild.id].markov_pings:
                    bc.config.discord.guilds[message.channel.guild.id].markov_pings = False
                    button.style = discord.ButtonStyle.red
                else:
                    bc.config.discord.guilds[message.channel.guild.id].markov_pings = True
                    button.style = discord.ButtonStyle.green
                await interaction.response.edit_message(content=header, view=self)
                await Msg.response(
                    message,
                    f"{message.author.mention} Markov pings are " + (
                        "enabled" if bc.config.discord.guilds[message.channel.guild.id].markov_pings
                        else "disabled"), silent)

        view = ConfigView()
        await Msg.response(message, header, silent=False, view=view)

    @staticmethod
    async def _config(message, command, silent=False):
        """Setup some channel specific configurations
    Examples:
        !config reactions <enable/disable>
        !config markovlog <enable/disable>
        !config responses <enable/disable>
        !config markovresponses <enable/disable>
        !config markovpings <enable/disable>"""
        if not await Util.check_args_count(message, command, silent, min=1, max=3):
            return
        if len(command) == 1:
            return await BuiltinCommands.__config_view(message, silent)
        elif len(command) == 3:
            if command[1] == "reactions":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist:
                        await Msg.response(
                            message, "Adding reactions is already enabled for this channel", silent)
                    else:
                        bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Adding reactions is successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist:
                        bc.config.discord.guilds[message.channel.guild.id].reactions_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Adding reactions is successfully disabled for this channel", silent)
                    else:
                        await Msg.response(
                            message, "Adding reactions is already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovlog":
                if command[2] in ("enable", "true", "on"):
                    if (message.channel.id
                            in bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist):
                        await Msg.response(
                            message, "Adding messages to Markov model is already enabled for this channel", silent)
                    else:
                        bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist.add(
                            message.channel.id)
                        await Msg.response(
                            message, "Adding messages to Markov model is successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if (message.channel.id
                            in bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist):
                        bc.config.discord.guilds[message.channel.guild.id].markov_logging_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Adding messages to Markov model is successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Adding messages to Markov model is already disabled for this channel", silent)
            elif command[1] == "responses":
                if command[2] in ("enable", "true", "on"):
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].responses_whitelist:
                        await Msg.response(
                            message, "Bot responses are already enabled for this channel", silent)
                    else:
                        bc.config.discord.guilds[message.channel.guild.id].responses_whitelist.add(message.channel.id)
                        await Msg.response(
                            message, "Bot responses are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if message.channel.id in bc.config.discord.guilds[message.channel.guild.id].responses_whitelist:
                        bc.config.discord.guilds[message.channel.guild.id].responses_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Bot responses are successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Bot responses are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovresponses":
                if command[2] in ("enable", "true", "on"):
                    if (message.channel.id
                            in bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist):
                        await Msg.response(
                            message, "Bot responses on mentioning are already enabled for this channel", silent)
                    else:
                        bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist.add(
                            message.channel.id)
                        await Msg.response(
                            message, "Bot responses on mentioning are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if (message.channel.id
                            in bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist):
                        bc.config.discord.guilds[message.channel.guild.id].markov_responses_whitelist.discard(
                            message.channel.id)
                        await Msg.response(
                            message, "Bot responses on mentioning are successfully disabled for this channel",
                            silent)
                    else:
                        await Msg.response(
                            message, "Bot responses on mentioning are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            elif command[1] == "markovpings":
                if command[2] in ("enable", "true", "on"):
                    if bc.config.discord.guilds[message.channel.guild.id].markov_pings:
                        await Msg.response(
                            message, "Markov pings are already enabled for this channel", silent)
                    else:
                        bc.config.discord.guilds[message.channel.guild.id].markov_pings = True
                        await Msg.response(
                            message, "Markov pings are successfully enabled for this channel", silent)
                elif command[2] in ("disable", "false", "off"):
                    if bc.config.discord.guilds[message.channel.guild.id].markov_pings:
                        bc.config.discord.guilds[message.channel.guild.id].markov_pings = False
                        await Msg.response(
                            message, "Markov pings are successfully disabled for this channel", silent)
                    else:
                        await Msg.response(
                            message, "Markov pings are already disabled for this channel", silent)
                else:
                    await Msg.response(message, "The third argument should be either 'enable' or 'disable'", silent)
            else:
                await Msg.response(message, f"Incorrect argument for command '{command[0]}'", silent)
        else:
            await Msg.response(message, f"Incorrect usage of command '{command[0]}'", silent)

    @staticmethod
    async def _silent(message, command, silent=False):
        """Make the following command silent (without any output to the chat)
    Example: !silent ping"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        command = command[1:]
        if command[0] not in bc.discord.commands.data.keys():
            await Msg.response(message, f"Unknown command '{command[0]}'", silent)
        else:
            cmd = bc.discord.commands.data[command[0]]
            message.content = message.content.split(' ', 1)[-1]
            await cmd.run(message, command, None, silent=True)

    @staticmethod
    async def _addalias(message, command, silent=False):
        """Add alias for commands
    Usage: !addalias <command> <alias>
    Example: !addalias ping pong"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        if command[1] not in bc.discord.commands.data.keys():
            return null(await Msg.response(message, f"Unknown command '{command[1]}'", silent))
        if command[2] in bc.discord.commands.data.keys():
            return null(await Msg.response(message, f"Command '{command[2]}' already exists", silent))
        if command[2] in bc.discord.commands.aliases.keys():
            return null(await Msg.response(message, f"Alias '{command[2]}' already exists", silent))
        bc.discord.commands.aliases[command[2]] = command[1]
        await Msg.response(message, f"Alias '{command[2]}' for '{command[1]}' was successfully created", silent)

    @staticmethod
    async def _delalias(message, command, silent=False):
        """Delete command alias
    Usage: !delalias <alias>
    Example: !delalias pong"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        if command[1] not in bc.discord.commands.aliases.keys():
            return null(await Msg.response(message, f"Alias '{command[1]}' does not exist", silent))
        bc.discord.commands.aliases.pop(command[1])
        await Msg.response(message, f"Alias '{command[1]}' was successfully deleted", silent)

    @staticmethod
    async def _listalias(message, command, silent=False):
        """Print list of aliases
    Example: !listalias"""
        if not await Util.check_args_count(message, command, silent, min=1, max=1):
            return
        result = ""
        alias_mapping = {}
        for alias, command in bc.discord.commands.aliases.items():
            if command not in alias_mapping.keys():
                alias_mapping[command] = []
            alias_mapping[command].append(alias)
        for command, aliases in alias_mapping.items():
            result += f"{', '.join(aliases)} -> {command}\n"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _avatar(message, command, silent=False):
        """Change bot avatar
    Example: !avatar <image>
    Hint: Use !listimg for list of available images"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        image = command[1]
        for root, _, files in os.walk(const.IMAGES_DIRECTORY):
            if not root.endswith(const.IMAGES_DIRECTORY):
                continue
            for file in files:
                if os.path.splitext(os.path.basename(file))[0].lower() == image.lower():
                    try:
                        with open(os.path.join(const.IMAGES_DIRECTORY, file), "rb") as f:
                            await bc.discord.bot_user.edit(avatar=f.read())
                        await Msg.response(
                            message, f"Successfully changed bot avatar to {image}", silent)
                    except discord.HTTPException as e:
                        await Msg.response(
                            message, f"Failed to change bot avatar.\nError: {e}", silent)
                    return
            else:
                hdr = {
                    "User-Agent": "Mozilla/5.0"
                }
                r = const.DISCORD_EMOJI_REGEX.match(image)
                if r is not None:
                    # Discord emoji
                    log.debug(f"Downloading https://cdn.discordapp.com/emojis/{r.group(2)}.png")
                    rq = urllib.request.Request(
                        f"https://cdn.discordapp.com/emojis/{r.group(2)}.png", headers=hdr)
                elif urllib.parse.urlparse(image).path.split('.')[-1] in ["jpg", "jpeg", "png", "ico", "gif", "bmp"]:
                    # Direct link to an image
                    rq = urllib.request.Request(image, headers=hdr)
                else:
                    # Not recognized source
                    break
                temp_image_file = tempfile.NamedTemporaryFile(dir=Util.tmp_dir(), delete=False)
                try:
                    with urllib.request.urlopen(rq) as response:
                        temp_image_file.write(response.read())
                except Exception as e:
                    log.error("Image downloading failed!", exc_info=True)
                    return null(await Msg.response(message, f"Image downloading failed: {e}", silent))
                finally:
                    temp_image_file.close()
                try:
                    with open(temp_image_file.name, "rb") as temp_image_file:
                        await bc.discord.bot_user.edit(avatar=temp_image_file.read())
                except Exception as e:
                    log.error("Changing avatar failed!", exc_info=True)
                    return null(await Msg.response(message, f"Changing avatar failed: {e}", silent))
                finally:
                    os.unlink(temp_image_file.name)
                return null(await Msg.response(message, f"Successfully changed bot avatar to {image}", silent))
        min_dist = 100000
        suggestion = ""
        for file in (os.path.splitext(os.path.basename(file))[0].lower() for file in files):
            dist = levenshtein_distance(image, file)
            if dist < min_dist:
                suggestion = file
                min_dist = dist
        await Msg.response(message, f"Image '{image}' is not found! Probably you meant '{suggestion}'", silent)

    @staticmethod
    async def _pin(message, command, silent=False):
        """Print pinned message by its index
    Example: !pin 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        index = await Util.parse_int_for_discord(
            message, command[1], "Message index should be an integer", silent)
        if index is None:
            return
        pins = await message.channel.pins()
        result = ""
        if 0 <= index < len(pins):
            result = pins[index].content + '\nBy ' + str(message.author)
        else:
            await Msg.response(message, "Invalid index of pinned message!", silent)
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _slowmode(message, command, silent=False):
        """Edit slowmode
    Example: !slowmode 0"""
        if not await Util.check_args_count(message, command, silent, min=2, max=2):
            return
        duration = await Util.parse_int_for_discord(
            message, command[1], f"Second parameter for '{command[0]}' should be duration in seconds", silent)
        if duration is None:
            return
        await message.channel.edit(slowmode_delay=duration)
        if duration == 0:
            await Msg.response(message, "Slowmode is disabled for current channel", silent)
        else:
            await Msg.response(message, f"Slowmode is set to {duration} seconds", silent)

    @staticmethod
    async def _permlevel(message, command, silent=False):
        """Get permission level for user
    Usage: !permlevel
           !permlevel `@user`"""
        if not await Util.check_args_count(message, command, silent, min=1, max=2):
            return
        info = ""
        user_id = 0
        if len(command) == 1:
            info = message.author
            user_id = message.author.id
        elif len(command) == 2:
            if not message.mentions:
                return null(
                    await Msg.response(message, "You need to mention the user "
                                                "for whom you want to get the permission level", silent))
            info = await message.guild.fetch_member(message.mentions[0].id)
            user_id = message.mentions[0].id
        if info is None or user_id not in bc.config.discord.users.keys():
            return null(await Msg.response(message, "Could not get permission level for this user", silent))
        perm_level = bc.config.discord.users[user_id].permission_level
        nick = str(info.nick) + " (" + str(info) + ")" if info.nick is not None else str(info)
        await Msg.response(message, f"Permission level for {nick} is {perm_level}", silent)

    @staticmethod
    async def _disabletl(message, command, silent=False):
        """Disable time limit for command
    Example: !disabletl ping"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        command = command[1:]
        if command[0] not in bc.discord.commands.data.keys():
            await Msg.response(message, f"Unknown command '{command[0]}'", silent)
        else:
            cmd = bc.discord.commands.data[command[0]]
            message.content = message.content.split(' ', 1)[-1]
            await cmd.run(message, command, bc.config.discord.users[message.author.id])
