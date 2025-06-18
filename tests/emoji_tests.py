from src.emoji import get_clock_emoji


@pytest.mark.parametrize("time_str, expected", [
    ("00:00", "🕛"),
    ("00:14", "🕛"),
    ("00:15", "🕧"),
    ("00:45", "🕐"),
    ("02:37", "🕝"),
    ("09:29", "🕤"),
    ("12:44", "🕧"),
    ("12:45", "🕐"),
    ("13:01", "🕐"),
    ("23:59", "🕛"),
])
def test_get_clock_emoji(time_str, expected):
    assert get_clock_emoji(time_str) == expected


@pytest.mark.parametrize("time_str", ["24:00", "12:60", "foo"])
def test_get_clock_emoji_invalid(time_str):
    assert get_clock_emoji(time_str) is None
