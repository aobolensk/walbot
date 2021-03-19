class Reminder:
    def __init__(self, time, message, channel_id, author_name, time_created):
        self.time = time
        self.message = message
        self.channel_id = channel_id
        self.ping_users = []
        self.whisper_users = []
        self.repeat_after = 0
        self.repeat_interval_measure = "minutes"
        self.author = author_name
        self.time_created = time_created

    def __eq__(self, time):
        return self.time == time

    def __lt__(self, time):
        return self.time < time

    def __gt__(self, time):
        return self.time > time
