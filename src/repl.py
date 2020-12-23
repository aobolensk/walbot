import inspect
import itertools
import threading
import socket

from src.config import bc
from src.log import log

REPL_HOST = ''


class REPLCommands:
    @staticmethod
    def help(message):
        commands = [func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
                    if not func[0].startswith('_')]
        return ', '.join(commands)

    @staticmethod
    def ping(message):
        return "Pong!"

    @staticmethod
    def channels(message):
        guilds = ((channel.id, channel.name) for channel in
                  itertools.chain.from_iterable(guild.text_channels for guild in bc.guilds))
        result = ""
        for guild in guilds:
            result += f"{guild[0]} -> {guild[1]}\n"
        return result


class Repl:
    def __init__(self, port) -> None:
        self.channel = None
        self.sock = None
        self.port = port
        thread = threading.Thread(target=self.start)
        thread.setDaemon(True)
        thread.start()

    def parse_command(self, message) -> str:
        message = message.split(' ')
        commands = [func[0] for func in inspect.getmembers(REPLCommands, inspect.isfunction)
                    if not func[0].startswith('_')]
        if message[0] in commands:
            return getattr(REPLCommands, message[0])(message).strip() + '\n'
        return "\n"

    def start(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR or socket.SO_REUSEPORT, 1)
        self.sock.bind((REPL_HOST, self.port))
        self.sock.listen()
        while True:
            log.debug(f"REPL initialized on port {self.port}")
            try:
                conn, addr = self.sock.accept()
                with conn:
                    log.debug(f"Connected by {addr}")
                    while True:
                        conn.send("> ".encode("utf-8"))
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.send(self.parse_command(data.decode("utf-8").strip()).encode("utf-8"))
            except OSError as e:
                log.warning(f"REPL: {e}")

    def stop(self):
        if self.sock:
            self.sock.close()
