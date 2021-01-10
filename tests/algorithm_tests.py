from src.algorithms import levenshtein_distance


def test_levenshtein_distance_from_equal_strings():
    assert levenshtein_distance("abc", "abc") == 0
