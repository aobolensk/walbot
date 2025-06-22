import asyncio
import sys

from src.shell import Shell


class DummyProcess:
    def __init__(self):
        self.kill_called = False
        self.wait_called = False
        self.returncode = 0

    async def communicate(self):
        await asyncio.sleep(3600)
        return b"", b""

    def kill(self):
        self.kill_called = True

    async def wait(self):
        self.wait_called = True
        self.returncode = -9


def test_run_async_terminates_on_timeout(monkeypatch):
    dummy_proc = DummyProcess()

    async def fake_create_subprocess_exec(*args, **kwargs):
        return dummy_proc

    async def fake_wait_for(*args, **kwargs):
        raise asyncio.exceptions.TimeoutError

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess_exec)
    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    result = asyncio.run(Shell.run_async("dummy"))

    assert result.exit_code == -1
    assert dummy_proc.kill_called
    assert dummy_proc.wait_called


PYTHON_ECHO = f'{sys.executable} -c "import sys;print(sys.argv[1])" "test"'


def test_run_async_shell_false_star():
    result = asyncio.run(Shell.run_async(PYTHON_ECHO))
    assert result.exit_code == 0
    assert result.stdout.strip() == 'test'


def test_run_async_shell_true_quotes_preserved():
    result = asyncio.run(Shell.run_async(PYTHON_ECHO, shell=True))
    assert result.exit_code == 0
    assert result.stdout.strip() == 'test'
