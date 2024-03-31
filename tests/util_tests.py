import asyncio

import pytest  # type:ignore

from src.utils import Util
from tests.fixtures.context import BufferTestExecutionContext


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


def test_parse_int(capsys):
    loop = asyncio.new_event_loop()
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "123", "Error 1"))
    assert value == 123
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "b123", "Error 2"))
    assert value is None
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "0123", "Error 3"))
    assert value == 123
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "0xf", "Error 4"))
    assert value is None
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "123b", "Error 5"))
    assert value is None
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "\n123", "Error 6"))
    assert value == 123
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "\n123\n", "Error 7"))
    assert value == 123
    value = loop.run_until_complete(Util.parse_int(BufferTestExecutionContext(), "\n1\n2\n", "Error 8"))
    assert value is None
    captured = capsys.readouterr()
    assert captured.out == (
        "Error 2\n"
        "Error 4\n"
        "Error 5\n"
        "Error 8\n"
    )


class TestPathToModule:
    @pytest.mark.parametrize("path,expected", [
        ("folder/subfolder/module.py", "folder.subfolder.module"),
        ("./folder/module.py", "folder.module"),
        ("/folder/subfolder/module.py", "folder.subfolder.module"),
        ("module.py", "module"),
        ("", ""),
    ])
    def test_path_to_module(self, path, expected):
        assert Util.path_to_module(path) == expected, f"Failed for path: {path}"
