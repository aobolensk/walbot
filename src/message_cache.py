from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CachedMsg:
    message: str
    author: str


class MessageCache:
    BUFFER_CAPACITY = 1001

    def __init__(self) -> None:
        self._data: Dict[str, List[CachedMsg]] = defaultdict(list)

    def push(self, channel_id: str, message: CachedMsg):
        self._data[channel_id].insert(0, message)
        self._data[channel_id] = self._data[channel_id][:self.BUFFER_CAPACITY]

    def get(self, channel_id: str, index: int):
        if channel_id not in self._data.keys():
            return
        if not 0 <= index < len(self._data[channel_id]):
            return
        return self._data[channel_id][index]

    def reset(self, channel_id: str, new_data: List[CachedMsg]):
        self._data[channel_id] = new_data
