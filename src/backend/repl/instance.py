import asyncio
import inspect
import socket

from src import const
from src.api.bot_instance import BotInstance
from src.backend.repl.cmd.builtin import REPLCommands
from src.config import bc
from src.log import log

REPL_HOST = ''


class ReplBotInstance(BotInstance):
    def __init__(self) -> None:
        self.channel = None
        self.sock = None

    async def parse_command(self, commands, message) -> str:
        args = message.split(' ')
        commands_list = [
            func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
            if not func[0].startswith('_')]
        if args[0] in commands_list:
            result = await getattr(commands, args[0])(args)
            result = result.strip() + '\n' if result else ""
            return result
        return ""

    def start(self, args, *rest, **kwargs) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        t = loop.create_task(self._run())
        loop.run_until_complete(t)

    async def _run(self) -> None:
        log.info("Starting REPL...")
        self.port = bc.config.repl["port"]
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR or socket.SO_REUSEPORT, 1)
        self.sock.bind((REPL_HOST, self.port))
        self.sock.setblocking(False)
        self.sock.listen()
        loop = asyncio.get_event_loop()
        log.debug(f"REPL initialized on port {self.port}")
        bc.be.set_running(const.BotBackend.REPL, True)
        while True:
            try:
                conn, addr = await loop.sock_accept(self.sock)
                with conn:
                    log.debug(f"Connected {addr[0]}:{addr[1]}")
                    commands = REPLCommands()
                    while True:
                        await loop.sock_sendall(conn, commands.prompt().encode("utf-8"))
                        data = await loop.sock_recv(conn, 1024)
                        if not data:
                            break
                        result = await self.parse_command(commands, data.decode("utf-8").strip())
                        await loop.sock_sendall(conn, result.encode("utf-8"))
                log.debug(f"Disconnected {addr[0]}:{addr[1]}")
            except OSError as e:
                log.warning(f"REPL: {e}")

    def stop(self, args, main_bot=True) -> None:
        if self.sock:
            self.sock.close()

    def has_credentials(self):
        return bc.config.repl["port"] is not None
