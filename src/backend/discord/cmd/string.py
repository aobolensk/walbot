"""Helper functions for working with strings"""

from src import const
from src.backend.discord.message import Msg
from src.commands import BaseCmd
from src.config import bc
from src.utils import Util, null


class StringCommands(BaseCmd):
    def bind(self):
        bc.discord.commands.register_commands(__name__, self.get_classname(), {
            "takechars": dict(permission=const.Permission.USER.value, subcommand=True),
            "dropchars": dict(permission=const.Permission.USER.value, subcommand=True),
            "countchars": dict(permission=const.Permission.USER.value, subcommand=True),
            "takewords": dict(permission=const.Permission.USER.value, subcommand=True),
            "dropwords": dict(permission=const.Permission.USER.value, subcommand=True),
            "countwords": dict(permission=const.Permission.USER.value, subcommand=True),
            "takelines": dict(permission=const.Permission.USER.value, subcommand=True),
            "droplines": dict(permission=const.Permission.USER.value, subcommand=True),
            "countlines": dict(permission=const.Permission.USER.value, subcommand=True),
            "tolower": dict(permission=const.Permission.USER.value, subcommand=True),
            "toupper": dict(permission=const.Permission.USER.value, subcommand=True),
            "join": dict(permission=const.Permission.USER.value, subcommand=True),
            "eqwords": dict(permission=const.Permission.USER.value, subcommand=True),
            "eqstrs": dict(permission=const.Permission.USER.value, subcommand=True),
        })

    @staticmethod
    async def _takechars(message, command, silent=False):
        """Take n characters of the string
    Examples:
        !takechars 2 hello
        Result: he
        !takechars -2 hello
        Result: lo"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:])
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = result[len(result) + num:]
        else:
            result = result[:num]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _dropchars(message, command, silent=False):
        """Drop n characters of the string
    Examples:
        !dropchars 2 hello
        Result: llo
        !dropchars -2 hello
        Result: hel"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:])
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = result[:len(result) + num]
        else:
            result = result[num:]
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countchars(message, command, silent=False):
        """Calculate length of the message
    Example: !countchars some text"""
        result = str(len(' '.join(command[1:])))
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _takewords(message, command, silent=False):
        """Take n words of the string
    Examples:
        !takewords 2 a b c
        Result: a b
        !takewords -2 a b c
        Result: b c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split()
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[len(result) + num:])
        else:
            result = ' '.join(result[:num])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _dropwords(message, command, silent=False):
        """Drop n words of the string
    Examples:
        !dropwords 2 a b c
        Result: c
        !dropwords -2 a b c
        Result: a"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split()
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = ' '.join(result[:len(result) + num])
        else:
            result = ' '.join(result[num:])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countwords(message, command, silent=False):
        """Count amount of words
    Example: !count some text"""
        result = str(len(' '.join(command).split()) - 1)
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _takelines(message, command, silent=False):
        """Take n lines of the string
    Examples:
        !takelines 2 a
        b
        c
        Result: a
        b
        !takelines -2 a
        b
        c
        Result: b
        c"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split('\n')
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[len(result) + num:])
        else:
            result = '\n'.join(result[:num])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _droplines(message, command, silent=False):
        """Drop n lines of the string
    Examples:
        !droplines 2 a
        b
        c
        Result: c
        !droplines -2 a
        b
        c
        Result: a"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        result = ' '.join(command[2:]).split('\n')
        num = await Util.parse_int_for_discord(
            message, command[1], f"Second argument of command '{command[0]}' should be an integer", silent)
        if num is None:
            return
        if num < 0:
            result = '\n'.join(result[:len(result) + num])
        else:
            result = '\n'.join(result[num:])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _countlines(message, command, silent=False):
        """Count amount of lines
    Example: !count some text"""
        result = str(len(' '.join(command).split('\n')))
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _tolower(message, command, silent=False):
        """Convert text to lower case
    Example: !tolower SoMe TeXt"""
        result = ' '.join(command[1:]).lower()
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _toupper(message, command, silent=False):
        """Convert text to upper case
    Example: !toupper SoMe TeXt"""
        result = ' '.join(command[1:]).upper()
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _join(message, command, silent=False):
        """Join words with string as separator
    Example: !join + 1 2 3 -> 1+2+3"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        separator = command[1]
        result = separator.join(command[2:])
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _eqwords(message, command, silent=False):
        """Check if two words are equal or not
    Example: !eqwords a b"""
        if not await Util.check_args_count(message, command, silent, min=3, max=3):
            return
        result = "true" if command[1] == command[2] else "false"
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _eqstrs(message, command, silent=False):
        """Check if two strings separated by ';' are equal or not
    Example: !eqstrs a;b"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        options = ' '.join(command[1:]).split(';')
        if len(options) < 2:
            return null(await Msg.response(message, "Too few options to compare", silent))
        if len(options) > 2:
            return null(await Msg.response(message, "Too many options to compare", silent))
        result = "true" if options[0] == options[1] else "false"
        await Msg.response(message, result, silent)
        return result
