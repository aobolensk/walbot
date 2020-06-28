import random
import re
import yaml

from . import const
from .log import log
from .config import bc


class MarkovNode:
    def __init__(self, node_type, word=None):
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
            return bc.markov.model[word]
        return bc.markov.end_node


class Markov:
    class NodeType:
        begin = 0
        word = 1
        end = 2

    def __init__(self):
        self.model = {"": MarkovNode(self.NodeType.begin)}
        self.end_node = MarkovNode(self.NodeType.end)
        self.filters = []
        self.version = const.MARKOV_CONFIG_VERSION

    def add_string(self, text):
        words = [word for word in filter(None, text.split(' ')) if not any(regex.match(word) for regex in self.filters)]
        current_node = self.model[""]
        for word in words:
            current_node.add_next(word)
            if word in self.model.keys():
                current_node = current_node.get_next(word)
            else:
                current_node = self.model[word] = MarkovNode(self.NodeType.word, word=word)
        if current_node != self.model[""]:
            current_node.add_next(None)

    def del_words(self, regex):
        removed = []
        for word in [word for word in self.model if re.search(regex, word)]:
            removed.append(self.model[word].word)
            del self.model[word]
        for _, node in self.model.items():
            for word in [word for word in node.next if word is not None and re.search(regex, word)]:
                node.del_next(word)
        return removed

    def find_words(self, regex):
        return [self.model[word].word for word in self.model if re.search(regex, word)]

    def generate(self, word=""):
        if word not in self.model.keys():
            return "<Empty message was generated>"
        current_node = self.model[word]
        result = word + ' '
        while current_node != self.end_node:
            index = random.randint(0, max(0, current_node.total_next - 1))
            s = 0
            for k, v in current_node.next.items():
                s += v
                if s > index:
                    result += (k if k is not None else "") + ' '
                    next_node = current_node.get_next(k)
                    if current_node == self.model[""] and next_node == self.end_node:
                        continue
                    current_node = next_node
                    break
            else:
                if current_node == self.model[""] and len(current_node.next.items()) == 1:
                    return "<Markov database is empty>"
                break
        result = result.strip()
        if not result:
            return "<Empty message was generated>"
        return result

    def gc(self, node=None):
        if not node:
            node = self.model[""]
        was = {node}
        for key in node.next.keys():
            next_node = node.get_next(key)
            if next_node not in was:
                was |= self.gc(next_node)
        if node == self.model[""]:
            result = []
            for node in set(list(self.model.values())).difference(was):
                if hasattr(node, "word"):
                    result.append(node.word)
                    del self.model[node.word]
            return result
        return was

    def serialize(self, filename, dumper=yaml.Dumper):
        with open(filename, 'wb') as f:
            f.write(yaml.dump(self, Dumper=dumper, encoding='utf-8', allow_unicode=True))
        log.info("Saving of Markov module data is finished")

    def check(self):
        for node in self.model.values():
            if sum(node.next.values()) != node.total_next:
                node.total_next = sum(node.next.values())
                return False
        return True
