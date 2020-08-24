import datetime


class Quote:
    def __init__(self, message, added_by):
        self.message = message
        self.author = ""
        self.added_by = added_by
        self.timestamp = datetime.datetime.now().replace(microsecond=0)

    def __str__(self):
        return self.quote()

    def get_author(self):
        return ("(c) " + self.author) if self.author else ""

    def quote(self):
        return f"{self.message} {self.get_author()}"

    def full_quote(self):
        return f"{self.message} {self.get_author()}\nAdded by: {self.added_by} at {self.timestamp}"
