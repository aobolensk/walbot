import asyncio

from src.test import BufferTestExecutionContext
from src.utils import Util


def test_cut_string():
    assert Util.cut_string("a" * 5, 6) == "a" * 5
    assert Util.cut_string("a" * 5, 5) == "a" * 5
    assert Util.cut_string("a" * 5, 4) == "a" + "..."
    assert Util.cut_string("a" * 5, 3) == "..."
    assert Util.cut_string("a" * 5, 2) == "..."
    assert Util.cut_string("a" * 5, 1) == "..."
    assert Util.cut_string("a" * 5, 0) == "..."
    assert Util.cut_string("abacaba", 100) == "abacaba"
    assert Util.cut_string("abacaba", 8) == "abacaba"
    assert Util.cut_string("abacaba", 7) == "abacaba"
    assert Util.cut_string("abacaba", 6) == "aba..."
    assert Util.cut_string("abacaba", 5) == "ab..."


def test_parse_int_for_command(capsys):
    loop = asyncio.new_event_loop()
    value = loop.run_until_complete(
        Util.parse_int_for_command(
            BufferTestExecutionContext(), "123", "Error 1"))
    assert value == 123
    value = loop.run_until_complete(
        Util.parse_int_for_command(
            BufferTestExecutionContext(), "b123", "Error 2"))
    assert value is None
    captured = capsys.readouterr()
    assert captured.out == (
        "Error 2\n"
    )
