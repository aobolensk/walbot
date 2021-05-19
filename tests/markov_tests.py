from src.markov import Markov


LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."


def test_markov_correctly_parses_sentence():
    markov = Markov()
    markov.add_string(LOREM)
    text = LOREM.split()
    for i in range(len(text) - 1):
        assert text[i + 1] in markov.model[text[i]].next.keys()
