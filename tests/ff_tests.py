import pytest

from src.ff import FF


@pytest.mark.parametrize("value, expected", [
    (None, False),
    ("1", True),
    ("ON", True),
    ("on", True),
    ("0", False),
    ("OFF", False),
])
def test_is_enabled(monkeypatch, value, expected):
    flag = "WALBOT_TEST_AUTO_UPDATE"
    if value is None:
        monkeypatch.delenv(flag, raising=False)
    else:
        monkeypatch.setenv(flag, value)
    assert FF.is_enabled(flag) is expected


def test_is_enabled_invalid():
    with pytest.raises(ValueError):
        FF.is_enabled("WALBOT_INVALID")


@pytest.mark.parametrize("value, expected", [
    ("abc", "abc"),
    ("", ""),
    (None, ""),
])
def test_get_value(monkeypatch, value, expected):
    flag = "WALBOT_TEST_AUTO_UPDATE"
    if value is None:
        monkeypatch.delenv(flag, raising=False)
    else:
        monkeypatch.setenv(flag, value)
    assert FF.get_value(flag) == expected


def test_get_value_invalid():
    with pytest.raises(ValueError):
        FF.get_value("WALBOT_INVALID")


def test_get_invalid_flags(monkeypatch):
    valid1 = "WALBOT_TEST_AUTO_UPDATE"
    valid2 = "WALBOT_FEATURE_MARKOV_MONGO"
    invalid1 = "WALBOT_INVALID1"
    invalid2 = "WALBOT_INVALID2"
    monkeypatch.setenv(valid1, "1")
    monkeypatch.setenv(valid2, "0")
    monkeypatch.setenv(invalid1, "x")
    monkeypatch.setenv(invalid2, "y")
    monkeypatch.setenv("OTHER_FLAG", "1")
    result = FF.get_invalid_flags()
    assert sorted(result) == [invalid1, invalid2]


def test_get_invalid_flags_no_invalid(monkeypatch):
    monkeypatch.setenv("WALBOT_TEST_AUTO_UPDATE", "1")
    monkeypatch.setenv("WALBOT_FEATURE_MARKOV_MONGO", "ON")
    monkeypatch.delenv("WALBOT_INVALID", raising=False)
    assert FF.get_invalid_flags() == []
