#!/usr/bin/env python3
"""
WalBot
Check out `python walbot.py -h` for list of available options
"""

import importlib
import os
import sys


def main():
    """WalBot launcher entrypoint"""
    if not ((3, 9) <= sys.version_info[:3] < (3, 14)):
        print("Python {}.{}.{} is not supported. You need Python 3.9 - 3.13".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        sys.exit(1)
    walbot_dir = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
    if os.path.normpath(os.getcwd()) != walbot_dir:
        os.chdir(walbot_dir)
    launcher = importlib.import_module("src.launcher").Launcher()
    err_code = launcher.launch_bot()
    sys.exit(err_code)


if __name__ == "__main__":
    main()
