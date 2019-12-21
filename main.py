import sys


class Launcher:
    def __init__(self, command):
        if command in [x for x in dir(self) if not x.startswith('_')]:
            getattr(self, command)()
        else:
            print("Invalid argument {}".format(command))
            self.help()

    def start(self):
        """Start the bot"""
        __import__("src.bot", fromlist=['object']).start()

    def stop(self):
        """Stop the bot"""
        __import__("src.bot", fromlist=['object']).stop()

    def restart(self):
        """Restart the bot"""
        bot = __import__("src.bot", fromlist=['object'])
        bot.stop()
        bot.start()

    def suspend(self):
        """Stop the main bot and start mini-bot"""
        __import__("src.bot", fromlist=['object']).stop()
        __import__("src.minibot", fromlist=['object']).start()

    def help(self):
        """Print help message"""
        print("Usage: " + sys.executable + ' ' + __file__ + " <action>")
        print("Possible actions:")
        for f in [x for x in dir(self) if not x.startswith('_')]:
            print("{} -> {}".format(f, getattr(self, f).__doc__))


def main():
    if len(sys.argv) == 2:
        Launcher(sys.argv[1])
    else:
        Launcher("help")


if __name__ == "__main__":
    main()
