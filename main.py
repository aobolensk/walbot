import sys

from src.bot import start, stop
from src.minibot import start as minibot_start


def help():
    print("Usage: " + sys.executable + ' ' + __file__ + " <action>\n\
    Possible actions:\n\
    start - start the bot\n\
    stop - stop the bot\n\
    restart - restart the bot\n\
    help - get this help list\n\
    ")


def main():
    if len(sys.argv) == 1:
        help()
    elif len(sys.argv) == 2:
        if sys.argv[1] == "start":
            start()
        elif sys.argv[1] == "stop":
            stop()
        elif sys.argv[1] == "restart":
            stop()
            start()
        elif sys.argv[1] == "suspend":
            stop()
            minibot_start()
        elif sys.argv[1] == "help":
            help()
        else:
            print("Unknown argument {}".format(sys.argv[1]))
    elif len(sys.argv) > 2:
        help()


if __name__ == "__main__":
    main()
