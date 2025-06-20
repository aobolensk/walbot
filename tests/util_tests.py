import asyncio
import os
import shutil
import tempfile

import pytest  # type:ignore
import requests  # type:ignore

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
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "123", "Error 1"))
    assert value == 123
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "b123", "Error 2"))
    assert value is None
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "0123", "Error 3"))
    assert value == 123
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "0xf", "Error 4"))
    assert value is None
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "123b", "Error 5"))
    assert value is None
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "\n123", "Error 6"))
    assert value == 123
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "\n123\n", "Error 7"))
    assert value == 123
    value = asyncio.run(Util.parse_int(BufferTestExecutionContext(), "\n1\n2\n", "Error 8"))
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


def test_request_get_file_creates_missing_dir(monkeypatch, tmp_path):
    class DummyResponse:
        status_code = 200
        content = b"file data"

    def dummy_get(*args, **kwargs):
        return DummyResponse()

    monkeypatch.setattr(requests, "get", dummy_get)
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))

    tmp_dir = tmp_path / "walbot"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)

    file_path = Util.request("http://example.com").get_file(".bin")

    assert tmp_dir.exists()
    assert os.path.isfile(file_path)
    with open(file_path, "rb") as f:
        assert f.read() == b"file data"
