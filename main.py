import sys


class Launcher:
    def __init__(self, command):
        if not (sys.version_info.major >= 3 and sys.version_info.minor >= 5):
            print("Python {}.{}.{} is not supported. You need Python 3.5+".format(
                sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
            exit(1)
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
        self.stop()
        __import__("src.bot", fromlist=['object']).start(main_bot=False)

    def help(self):
        """Print help message"""
        print("Usage: " + sys.executable + ' ' + __file__ + " <action>", file=sys.stderr)
        print("Possible actions:", file=sys.stderr)
        for f in [x for x in dir(self) if not x.startswith('_')]:
            print("{} -> {}".format(f, getattr(self, f).__doc__), file=sys.stderr)


def main():
    if len(sys.argv) == 2:
        Launcher(sys.argv[1])
    else:
        Launcher("help")


if __name__ == "__main__":
    main()
