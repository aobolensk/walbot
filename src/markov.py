import random
import yaml


class MarkovNode:
    def __init__(self, markov, node_type, word=None):
        self.markov = markov
        self.type = node_type
        if self.type == Markov.NodeType.word:
            self.word = word
        self.next = {None: 0}
        self.total_next = 0

    def add_next(self, word):
        if word in self.next.keys():
            self.next[word] += 1
        else:
            self.next[word] = 1

    def get_next(self, word):
        if word is not None:
            return self.markov.model[word]
        else:
            return self.markov.end_node
        self.total_next += 1


class Markov:
    class NodeType:
        begin = 0
        word = 1
        end = 2

    def __init__(self):
        self.model = {"": MarkovNode(self, self.NodeType.begin)}
        self.end_node = MarkovNode(self, self.NodeType.end)

    def add_string(self, text):
        words = text.split()
        words = filter(None, words)
        current_node = self.model[""]
        for word in words:
            current_node.add_next(word)
            if word in self.model.keys():
                current_node = current_node.get_next(word)
            else:
                current_node = self.model[word] = MarkovNode(
                    self, self.NodeType.word, word=word
                )
        current_node.add_next(None)

    def generate(self):
        current_node = self.model[""]
        result = ""
        while current_node != self.end_node:
            index = random.randint(0, max(0, current_node.total_next - 1))
            s = 0
            for k, v in current_node.next.items():
                s += v
                if s > index:
                    result += (k if k is not None else "") + ' '
                    current_node = current_node.get_next(k)
                    break
            else:
                if len(current_node.next.items()) > 0:
                    return "<Markov database is empty>"
        return result.strip()

    def serialize(self, filename):
        with open(filename, 'wb') as f:
            f.write(yaml.dump(self, encoding='utf-8'))
