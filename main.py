import sys


class Launcher:
    def __init__(self, command):
        if command in [x for x in dir(self) if not x.startswith('_')]:
            getattr(self, command)()
        else:
            print("Invalid argument {}".format(command))

    def start(self):
        __import__("src.bot", fromlist=['object']).start()

    def stop(self):
        __import__("src.bot", fromlist=['object']).stop()

    def restart(self):
        __import__("src.bot", fromlist=['object']).stop()
        __import__("src.bot", fromlist=['object']).start()

    def suspend(self):
        __import__("src.bot", fromlist=['object']).stop()
        __import__("src.minibot", fromlist=['object']).start()

    def help(self):
        print("\
    Usage: " + sys.executable + ' ' + __file__ + " <action>\n\
    Possible actions:\n\
    start - start the bot\n\
    stop - stop the bot\n\
    restart - restart the bot\n\
    help - get this help list\n\
    ")


def main():
    if len(sys.argv) == 2:
        Launcher(sys.argv[1])
    else:
        Launcher("help")


if __name__ == "__main__":
    main()
