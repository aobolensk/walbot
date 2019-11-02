import sys

import bot

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
            bot.start()
        elif sys.argv[1] == "stop":
            bot.stop()
        elif sys.argv[1] == "help":
            help()
        else:
            print("Unknown argument {}".format(sys.argv[1]))
    elif len(sys.argv) > 2:
        help()


if __name__ == "__main__":
    main()
