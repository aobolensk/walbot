from src.markov import Markov

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
    "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)


def test_markov_correctly_parses_sentence():
    markov = Markov()
    markov.add_string(LOREM)
    text = LOREM.split()
    for i in range(len(text) - 1):
        assert text[i + 1] in markov.model[text[i]].next.keys()


def test_markov_correctly_deletes_word():
    markov = Markov()
    markov.add_string(LOREM)
    markov.del_words("ipsum")
    assert "ipsum" not in markov.model["Lorem"].next.keys()
    assert "ipsum" not in markov.model.keys()


def test_markov_correctly_deletes_word_with_regex():
    markov = Markov()
    markov.add_string(LOREM)
    markov.del_words("^[a-z]{3}$")
    assert "sit" not in markov.model["dolor"].next.keys()
    assert "sed" not in markov.model["elit,"].next.keys()
    assert "ipsum" in markov.model["Lorem"].next.keys()
    assert "ut" in markov.model["incididunt"].next.keys()


def test_markov_correctly_finds_word():
    markov = Markov()
    markov.add_string(LOREM)
    found = markov.find_words("^[a-z]{3}$")
    assert "sit" in found
    assert "sed" in found
    assert "ipsum" not in found
    assert "ut" not in found


def test_markov_check():
    markov = Markov()
    markov.add_string(LOREM)
    assert markov.check() is True


def test_markov_check_broken():
    markov = Markov()
    markov.add_string(LOREM)
    markov.model[""].total_next = 0  # break next count for initial node
    assert markov.check() is False


def test_get_next_words_list_returns_sorted_counts():
    markov = Markov()
    markov.add_string("hello world hello world hello friend")
    words = markov.get_next_words_list("hello")
    assert words == [("world", 2), ("friend", 1)]
