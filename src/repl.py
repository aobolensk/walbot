import asyncio
import inspect
import itertools
import socket

from src.config import bc
from src.log import log

REPL_HOST = ''


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
        commands = [func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
                    if not func[0].startswith('_')]
        return ', '.join(commands)

    async def ping(self, command):
        """Ping the bot"""
        return "Pong!"

    async def channels(self, command):
        """Print list of the channels bot is connected to"""
        guilds = ((channel.id, channel.name) for channel in
                  itertools.chain.from_iterable(guild.text_channels for guild in bc.guilds))
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
            self._current_channel = await bc.fetch_channel(int(channel))
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
        await self._current_channel.send(text)


class Repl:
    def __init__(self, port) -> None:
        self.channel = None
        self.sock = None
        self.port = port

    async def parse_command(self, commands, message) -> str:
        args = message.split(' ')
        commands_list = [
            func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
            if not func[0].startswith('_')]
        if args[0] in commands_list:
            result = await getattr(commands, args[0])(args) or ""
            return result.strip() + '\n'
        return "\n"

    async def start(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR or socket.SO_REUSEPORT, 1)
        self.sock.bind((REPL_HOST, self.port))
        self.sock.setblocking(False)
        self.sock.listen()
        loop = asyncio.get_event_loop()
        log.debug(f"REPL initialized on port {self.port}")
        while True:
            try:
                conn, addr = await loop.sock_accept(self.sock)
                with conn:
                    log.debug(f"Connected by {addr}")
                    commands = REPLCommands()
                    while True:
                        await loop.sock_sendall(conn, commands.prompt().encode("utf-8"))
                        data = await loop.sock_recv(conn, 1024)
                        if not data:
                            break
                        result = await self.parse_command(commands, data.decode("utf-8").strip())
                        await loop.sock_sendall(conn, result.encode("utf-8"))
            except OSError as e:
                log.warning(f"REPL: {e}")

    def stop(self):
        if self.sock:
            self.sock.close()
