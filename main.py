import sys


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
            __import__("src.bot", fromlist=['object']).start()
        elif sys.argv[1] == "stop":
            __import__("src.bot", fromlist=['object']).stop()
        elif sys.argv[1] == "restart":
            __import__("src.bot", fromlist=['object']).stop()
            __import__("src.bot", fromlist=['object']).start()
        elif sys.argv[1] == "suspend":
            __import__("src.bot", fromlist=['object']).stop()
            __import__("src.minibot", fromlist=['object']).start()
        elif sys.argv[1] == "help":
            help()
        else:
            print("Unknown argument {}".format(sys.argv[1]))
    elif len(sys.argv) > 2:
        help()


if __name__ == "__main__":
    main()
