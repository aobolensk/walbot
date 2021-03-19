import datetime
import dateutil.relativedelta

from src.log import log


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

    def get_next_event_delta(self):
        if self.repeat_interval_measure == "minutes":
            return datetime.datetime.timedelta(minutes=self.repeat_after)
        if self.repeat_interval_measure == "months":
            return dateutil.relativedelta.relativedelta(months=self.repeat_after)
        if self.repeat_interval_measure == "years":
            return dateutil.relativedelta.relativedelta(years=self.repeat_after)
        else:
            log.error(f"Unknown repeat_interval_measure: {self.repeat_interval_measure}")
            return datetime.datetime.timedelta(minutes=0)

    def __eq__(self, time):
        return self.time == time

    def __lt__(self, time):
        return self.time < time

    def __gt__(self, time):
        return self.time > time
