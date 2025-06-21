import asyncio
import sys

from src.shell import Shell


PYTHON_ECHO = f'{sys.executable} -c "import sys;print(sys.argv[1])" "*"'


def test_run_shell_false_star():
    result = Shell.run(PYTHON_ECHO)
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_shell_true_quotes_preserved():
    result = Shell.run(PYTHON_ECHO, shell=True)
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_async_shell_false_star():
    result = asyncio.run(Shell.run_async(PYTHON_ECHO))
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_async_shell_true_quotes_preserved():
    result = asyncio.run(Shell.run_async(PYTHON_ECHO, shell=True))
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'
