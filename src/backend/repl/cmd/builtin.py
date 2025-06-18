import inspect
import itertools

from src.config import bc


class REPLCommands:
    def _build_prompt(self) -> str:
        prompt = ""
        if self._current_channel is not None:
            prompt = str(self._current_channel)
        prompt += "> "
        return prompt

    def __init__(self) -> None:
        self._current_channel = None
        self.prompt = self._build_prompt

    async def help(self, command):
        """Print list of the commands"""
        commands = [
            f"{func[0]} -> {func[1].__doc__ or ''}" for func in inspect.getmembers(REPLCommands, inspect.isfunction)
            if not func[0].startswith('_')]
        return '\n'.join(commands)

    async def ping(self, command):
        """Ping the bot"""
        return "Pong!"

    async def channels(self, command):
        """Print list of the channels bot is connected to"""
        guilds = ((channel.id, channel.name) for channel in
                  itertools.chain.from_iterable(guild.text_channels for guild in bc.discord.guilds))
        result = ""
        for guild in guilds:
            result += f"{guild[0]} -> {guild[1]}\n"
        return result

    async def join(self, command):
        """Join specific channel"""
        if len(command) < 2:
            return "Usage: join <channel_id>"
        channel = command[1]
        try:
            self._current_channel = bc.discord.get_channel(int(channel))
        except Exception as e:
            return f"Failed to join channel: {e}"
        return "Joined channel: " + str(self._current_channel)

    async def part(self, command):
        """Part channel"""
        self._current_channel = None

    async def echo(self, command):
        """Send message to joined channel"""
        if len(command) < 2:
            return "Usage: echo <message>"
        text = ' '.join(command[1:])
        if self._current_channel is None:
            return "Cannot send message to undefined channel. First execute: join <channel_id>"
        t = bc.discord.background_loop.create_task(self._current_channel.send(text))
        bc.discord.background_loop.run_until_complete(t)
