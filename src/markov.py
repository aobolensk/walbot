import random
import re
from enum import IntEnum
from typing import List, Optional, Set

import yaml

from src import const
from src.ff import FF


class MarkovNode:
    def __init__(self, node_type, word: str = None):
        self.type = node_type
        self.word = word
        if not FF.is_enabled("WALBOT_FEATURE_MARKOV_MONGO"):
            self.next = {None: 0}
        else:
            self.next = {"__markov_null": 0}
        self.total_next = 0

    def add_next(self, word: str) -> None:
        if word in self.next.keys():
            self.next[word] += 1
        else:
            self.next[word] = 1
        self.total_next += 1

    def del_next(self, word: str) -> None:
        if word in self.next.keys():
            self.total_next -= self.next[word]
            del self.next[word]

    def get_next(self, model: 'Markov', word: str) -> str:
        if not FF.is_enabled("WALBOT_FEATURE_MARKOV_MONGO"):
            if word is not None:
                return model.model[word]
        else:
            if word != "__markov_null":
                return model.model[word]
        return model.end_node


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
        self.min_chars = 10
        self.min_words = 2
        self.max_chars = 2000
        self.max_words = 500
        self.chains_generated = 0
        self.ignored_prefixes = dict()

    def add_string(self, text: str) -> None:
        if len(text) < self.min_chars or len(text) > self.max_chars:
            return
        words = [word for word in filter(None, text.split(' ')) if not any(regex.match(word) for regex in self.filters)]
        if len(words) < self.min_words or len(words) > self.max_words:
            return
        current_node = self.model[""]
        for word in words:
            current_node.add_next(word)
            if word in self.model.keys():
                current_node = current_node.get_next(self, word)
            else:
                current_node = self.model[word] = MarkovNode(self.NodeType.word, word=word)
        if current_node != self.model[""]:
            current_node.add_next(None)

    def del_words(self, regex: str) -> List[str]:
        removed = []
        for word in [word for word in self.model if re.search(regex, word)]:
            removed.append(self.model[word].word)
            del self.model[word]
        for _, node in self.model.items():
            for word in [word for word in node.next if word is not None and re.search(regex, word)]:
                node.del_next(word)
        return removed

    def find_words(self, regex: str) -> List[str]:
        return [self.model[word].word for word in self.model if re.search(regex, word)]

    def get_next_words_list(self, word: str) -> List[str]:
        if word not in self.model.keys():
            return []
        return sorted(self.model[word].next.items(), key=lambda x: -x[1])

    def generate(self, word: str = "") -> str:
        if word not in self.model.keys():
            return "<Empty message was generated>"
        current_node = self.model[word]
        result = word + ' '
        while current_node != self.end_node:
            index = random.randint(0, max(0, current_node.total_next - 1))
            count = 0
            for word, next_count in current_node.next.items():
                count += next_count
                if count > index:
                    result += (word if word is not None else "") + ' '
                    next_node = current_node.get_next(self, word)
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
        self.chains_generated += 1
        return result

    def collect_garbage(self, node: Optional[MarkovNode] = None) -> Set[str]:
        if not node:
            node = self.model[""]
        was = {node}
        for key in node.next.keys():
            next_node = node.get_next(key)
            if next_node not in was:
                was |= self.collect_garbage(next_node)
        if node == self.model[""]:
            result = []
            for node in set(self.model.values()).difference(was):
                if hasattr(node, "word"):
                    result.append(node.word)
                    del self.model[node.word]
            return result
        return was

    def serialize(self, filename: str, dumper: type = yaml.Dumper) -> None:
        with open(filename, 'wb') as markov_file:
            markov_file.write(yaml.dump(self, Dumper=dumper, encoding='utf-8', allow_unicode=True))

    def check(self) -> bool:
        for node in self.model.values():
            if sum(node.next.values()) != node.total_next:
                node.total_next = sum(node.next.values())
                return False
        return True


class MarkovV2:
    class NodeType(IntEnum):
        begin = 0
        word = 1
        end = 2

    def __init__(self, col):
        self.version = const.MARKOV_CONFIG_VERSION
        self._collection = col

    def get(self, key: str):
        return self._collection.find_one({})[key]

    def add_next(self, node, word: str) -> None:
        if word in node["next"].keys():
            node["next"][word] += 1
        else:
            node["next"][word] = 1
            if word != "__markov_terminate":
                self._collection.update_one(
                    {"model": {'$exists': 1}},
                    {"$set": {f"model.{word}": {
                        "word": word,
                        "next": {
                            "__markov_null": 0,
                        },
                        "total_next": 0,
                        "type": self.NodeType.word,
                    }
                    }}
                )
        node["total_next"] += 1
        self._collection.update_one(
            {"model": {'$exists': 1}},
            {"$set": {f"model.{node['word'] or '__markov_null'}": node}}
        )

    def del_next(self, node, word: str) -> None:
        pass

    def get_next(self, word: str):
        res = self._collection.find_one(
            {f"model.{word}": {'$exists': 1}},
            {f"model.{word}": 1}
        )
        if res is None:
            res = self._collection.find_one(
                {"end_node": {'$exists': 1}},
                {"end_node": 1}
            )
            return res["end_node"]
        return res["model"][word]

    def preprocess_key(key: str):
        return key.replace("$", "<__markov_dollar>").replace(".", "<__markov_dot>")

    def postprocess_key(key: str):
        return key.replace("<__markov_dollar>", "$").replace("<__markov_dot>", ".")

    def add_string(self, text: str) -> None:
        if len(text) < self.get("min_chars") or len(text) > self.get("max_chars"):
            return
        words = [
            word
            for word in filter(None, text.split(' '))
            if not any(regex.match(word) for regex in self.get("filters"))
        ]
        if len(words) < self.get("min_words") or len(words) > self.get("max_words"):
            return
        current_node = self.get_next("__markov_null")
        for word in words:
            self.add_next(current_node, word)
            current_node = self.get_next(word)
        if current_node["word"] is not None:
            self.add_next(current_node, "__markov_terminate")

    def del_words(self, regex: str) -> List[str]:
        removed = []
        for word in [word for word in self.model if re.search(regex, word)]:
            removed.append(self.model[word].word)
            del self.model[word]
        for _, node in self.model.items():
            for word in [word for word in node.next if word is not None and re.search(regex, word)]:
                node.del_next(word)
        return removed

    def find_words(self, regex: str) -> List[str]:
        return [self.model[word].word for word in self.model if re.search(regex, word)]

    def generate(self, word: str = "__markov_null") -> str:
        current_node = self.get_next(word)
        if current_node is None:
            return "<Empty message was generated>"
        result = ""
        while current_node["type"] != self.NodeType.end:
            index = random.randint(0, max(0, current_node["total_next"] - 1))
            count = 0
            for word, next_count in current_node["next"].items():
                count += next_count
                if count > index:
                    result += (word if word != "__markov_terminate" else "") + ' '
                    print("result:", result)
                    next_node = self.get_next(word)
                    if current_node["word"] is None and next_node["type"] == self.NodeType.end:
                        continue
                    current_node = next_node
                    break
            else:
                if current_node["word"] is None and len(current_node["next"].items()) == 1:
                    return "<Markov database is empty>"
                break
        result = result.strip()
        if not result:
            return "<Empty message was generated>"
        # self.chains_generated += 1
        return result

    def collect_garbage(self, node: Optional[MarkovNode] = None) -> Set[str]:
        pass

    def serialize(self, filename: str, dumper: type = yaml.Dumper) -> None:
        pass

    def check(self) -> bool:
        return True
