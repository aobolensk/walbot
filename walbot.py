#!/usr/bin/env python3
"""
WalBot
Check out `python walbot.py -h` for list of available options
"""

import importlib
import sys


def main():
    """WalBot launcher entrypoint"""
    if not (sys.version_info.major >= 3 and sys.version_info.minor >= 6):
        print("Python {}.{}.{} is not supported. You need Python 3.6+".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        sys.exit(1)
    importlib.import_module("src.launcher").Launcher()


if __name__ == "__main__":
    main()
