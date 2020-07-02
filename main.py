import argparse
import sys


class Launcher:
    def __init__(self):
        parser = argparse.ArgumentParser(description='WalBot', formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("action", choices=[x for x in dir(self) if not x.startswith('_')], help='Action for bot')
        parser.add_argument("--fast_start", action="store_true",
                            help="Disable some things to make bot start faster:\n" +
                                 "- Disable Markov model check on start\n")
        parser.add_argument("--patch", action="store_true",
                            help="Call script for patching config files before starting the bot")
        if sys.platform in ("linux", "darwin"):
            parser.add_argument("--nohup", action="store_true", help="Ignore SIGHUP and redirect output to nohup.out")
        self.args = parser.parse_args()
        getattr(self, self.args.action)()

    def start(self):
        """Start the bot"""
        __import__("src.bot", fromlist=['object']).start(self.args)

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


def main():
    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 5):
        print("Python {}.{}.{} is not supported. You need Python 3.5+".format(
              sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        sys.exit(1)
    Launcher()


if __name__ == "__main__":
    main()
