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
        """Insert a new message to the beginning of the channel buffer.

        Parameters
        ----------
        channel_id:
            Identifier of the channel where the message was sent.
        message:
            ``CachedMsg`` instance representing the message to store.
        """
        self._data[channel_id].insert(0, message)
        self._data[channel_id] = self._data[channel_id][:self.BUFFER_CAPACITY]

    def get(self, channel_id: str, index: int):
        """Return cached message by index or ``None`` if unavailable.

        Parameters
        ----------
        channel_id:
            Identifier of the channel.
        index:
            Position of the message in the channel buffer. ``0`` is the most
            recent message.
        """
        if channel_id not in self._data.keys():
            return
        if not 0 <= index < len(self._data[channel_id]):
            return
        return self._data[channel_id][index]

    def reset(self, channel_id: str, new_data: List[CachedMsg]):
        """Replace stored messages for a channel.

        Parameters
        ----------
        channel_id:
            Identifier of the channel.
        new_data:
            List of ``CachedMsg`` objects that becomes the new buffer value.
        """
        self._data[channel_id] = new_data
