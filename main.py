import sys

from src.bot import start, stop

def help():
    print("Usage: " + sys.executable + ' ' + __file__ + " <action>\n\
    Possible actions:\n\
    start - start the bot\n\
    stop - stop the bot\n\
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
        elif sys.argv[1] == "help":
            help()
        else:
            print("Unknown argument {}".format(sys.argv[1]))
    elif len(sys.argv) > 2:
        help()


if __name__ == "__main__":
    main()
