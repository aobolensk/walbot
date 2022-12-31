class MessageCache:
    BUFFER_CAPACITY = 1001

    def __init__(self) -> None:
        self._data = dict()

    def push(self, message):
        if message.channel.id not in self._data.keys():
            self._data[message.channel.id] = []
        self._data[message.channel.id].insert(0, message)
        self._data[message.channel.id] = self._data[message.channel.id][:self.BUFFER_CAPACITY]

    def get(self, channel_id, index):
        if channel_id not in self._data.keys():
            return
        if not 0 <= index < len(self._data[channel_id]):
            return
        return self._data[channel_id][index]

    def reset(self, channel_id, new_data):
        self._data[channel_id] = new_data
