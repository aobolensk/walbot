from src.utils import Time


class Quote:
    def __init__(self, message, added_by):
        self.message = message
        self.author = ""
        self.added_by = added_by
        self.timestamp = Time().now()

    def __str__(self):
        return self.quote()

    def get_author(self):
        return ("(c) " + self.author) if self.author else ""

    def quote(self):
        return f"{self.message} {self.get_author()}"

    def full_quote(self):
        return f"{self.message} {self.get_author()}\nAdded by: {self.added_by[:-5]} at {self.timestamp}"
