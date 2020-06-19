import argparse
import sys


class Launcher:
    def __init__(self):
        parser = argparse.ArgumentParser(description='WalBot')
        parser.add_argument("action", choices=[x for x in dir(self) if not x.startswith('_')], help='Action for bot')
        args = parser.parse_args()
        getattr(self, args.action)()

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
    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 5):
        print("Python {}.{}.{} is not supported. You need Python 3.5+".format(
              sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        exit(1)
    Launcher()


if __name__ == "__main__":
    main()
