import os
import subprocess
import sys

from src.api.execution_context import ExecutionContext


class BufferTestExecutionContext(ExecutionContext):
    def __init__(self) -> None:
        super().__init__()
        self.platform = "test"

    async def send_message(self, message: str, *args, **kwargs) -> None:
        print(message)

    def disable_pings(self, message: str) -> None:
        return message

    def message_author(self) -> None:
        return ""


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
    subprocess.call(
        pytest_args,
        env={
            "PYTHON_PATH": os.getcwd()
        },
    )
