import asyncio

from src.shell import Shell


def test_run_shell_false_star():
    result = Shell.run('echo "*"')
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_shell_true_quotes_preserved():
    result = Shell.run('echo "*"', shell=True)
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_async_shell_false_star():
    result = asyncio.run(Shell.run_async('echo "*"'))
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'


def test_run_async_shell_true_quotes_preserved():
    result = asyncio.run(Shell.run_async('echo "*"', shell=True))
    assert result.exit_code == 0
    assert result.stdout.strip() == '*'
