import os
import subprocess
import sys

from src.api.execution_context import ExecutionContext


class BufferTestExecutionContext(ExecutionContext):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "test"

    async def send_message(self, message: str, *args, **kwargs) -> None:
        if self.silent:
            return
        print(message)

    def disable_pings(self, message: str) -> str:
        return message

    def message_author(self) -> str:
        return ""

    def message_author_id(self) -> int:
        return 0

    def channel_name(self) -> str:
        return "console"

    def channel_id(self) -> int:
        return 0


def start_testing(args):
    if args.verbose2:
        args.verbose = True
    pytest_args = []
    pytest_args.append(sys.executable)
    pytest_args.append("-m")
    pytest_args.append("pytest")
    if args.verbose:
        pytest_args.append("-v")
    if args.verbose2:
        pytest_args.append("--capture=tee-sys")  # Capture and print stdout/stderr
    ret_code = subprocess.call(
        pytest_args,
        env={
            "PYTHON_PATH": os.getcwd()
        },
    )
    return ret_code
