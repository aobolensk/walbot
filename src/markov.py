import random
import re
import yaml

from .log import log


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
        self.total_next += 1

    def del_next(self, word):
        if word in self.next.keys():
            self.total_next -= self.next[word]
            del self.next[word]

    def get_next(self, word):
        if word is not None:
            return self.markov.model[word]
        else:
            return self.markov.end_node


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

    def del_words(self, regex):
        total_removed = 0
        for word in [word for word in self.model if re.search(regex, word)]:
            del self.model[word]
            total_removed += 1
        for _, node in self.model.items():
            for word in [word for word in node.next if word is not None and re.search(regex, word)]:
                node.del_next(word)
        return total_removed

    def generate(self):
        current_node = self.model[""]
        result = ""
        attempt = 0
        while len(result) == 0 and attempt < 5:
            attempt += 1
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

    def serialize(self, filename, dumper=yaml.Dumper):
        with open(filename, 'wb') as f:
            f.write(yaml.dump(self, Dumper=dumper, encoding='utf-8'))
        log.info("Saving of Markov module data is finished")
