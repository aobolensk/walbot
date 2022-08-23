from src.api.execution_context import ExecutionContext
from src.cmd.builtin import BuiltinCommands
from src.config import bc


class BufferTestExecutionContext(ExecutionContext):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "test"

    def send_message(self, message: str, *args, **kwargs) -> None:
        print(message)

    def disable_pings(self, message: str) -> None:
        return message


def test_empty_executor():
    assert bc.executor.commands == dict()


def test_ping_command(capsys):
    bc.executor.commands = dict()
    bc.executor.add_module(BuiltinCommands())
    bc.executor.commands["ping"].run(["ping"], BufferTestExecutionContext())
    captured = capsys.readouterr()
    assert captured.out == "Pong!\n"
