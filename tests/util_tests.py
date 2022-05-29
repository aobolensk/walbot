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
