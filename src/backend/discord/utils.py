from src.backend.discord.message import Msg


class DiscordUtil:
    @staticmethod
    async def check_args_count(message, command, silent, min=None, max=None):
        if min and len(command) < min:
            await Msg.response(message, f"Too few arguments for command '{command[0]}'", silent)
            return False
        if max and len(command) > max:
            await Msg.response(message, f"Too many arguments for command '{command[0]}'", silent)
            return False
        return True

    @staticmethod
    async def parse_int_for_discord(message, string, error_message, silent):
        try:
            return int(string)
        except ValueError:
            await Msg.response(message, error_message, silent)
            return
