from src.algorithms import levenshtein_distance


def test_levenshtein_distance_from_equal_strings():
    assert levenshtein_distance("abc", "abc") == 0

def test_levenshtein_distance_difference_1():
    assert levenshtein_distance("aac", "abc") == 1
    assert levenshtein_distance("abc", "aac") == 1

def test_levenshtein_distance_different_length():
    assert levenshtein_distance("ab", "abc") == 1
    assert levenshtein_distance("abc", "ab") == 1
    assert levenshtein_distance("a", "abc") == 2
    assert levenshtein_distance("abc", "a") == 2

def test_levenshtein_distance_swapped_letters():
    assert levenshtein_distance("help", "hepl") == 2
