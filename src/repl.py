import asyncio
import inspect
import itertools
import socket

from src.config import bc
from src.log import log

REPL_HOST = ''


class REPLCommands:
    async def help(self, message):
        commands = [func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
                    if not func[0].startswith('_')]
        return ', '.join(commands)

    async def ping(self, message):
        return "Pong!"

    async def channels(self, message):
        guilds = ((channel.id, channel.name) for channel in
                  itertools.chain.from_iterable(guild.text_channels for guild in bc.guilds))
        result = ""
        for guild in guilds:
            result += f"{guild[0]} -> {guild[1]}\n"
        return result

    async def echo(self, message):
        if len(message) < 3:
            return "Usage: echo <channel_id> <message>"
        channel = message[1]
        text = ' '.join(message[2:])
        channel = await bc.fetch_channel(int(channel))
        await channel.send(text)


class Repl:
    def __init__(self, port) -> None:
        self.channel = None
        self.sock = None
        self.port = port
        self.commands = REPLCommands()

    async def parse_command(self, message) -> str:
        message = message.split(' ')
        commands = [func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
                    if not func[0].startswith('_')]
        if message[0] in commands:
            result = await getattr(self.commands, message[0])(message) or ""
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
                    while True:
                        await loop.sock_sendall(conn, "> ".encode("utf-8"))
                        data = await loop.sock_recv(conn, 1024)
                        if not data:
                            break
                        result = await self.parse_command(data.decode("utf-8").strip())
                        await loop.sock_sendall(conn, result.encode("utf-8"))
            except OSError as e:
                log.warning(f"REPL: {e}")

    def stop(self):
        if self.sock:
            self.sock.close()
