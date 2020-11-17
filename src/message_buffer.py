class MessageBuffer:
    BUFFER_CAPACITY = 1001

    def __init__(self) -> None:
        self.data = dict()

    def push(self, message):
        if message.channel.id not in self.data.keys():
            self.data[message.channel.id] = []
        self.data[message.channel.id].insert(0, message)
        self.data[message.channel.id] = self.data[message.channel.id][:self.BUFFER_CAPACITY]

    def get(self, channel_id, index):
        if channel_id not in self.data.keys():
            return
        if not 0 <= index < len(self.data[channel_id]):
            return
        return self.data[channel_id][index]
