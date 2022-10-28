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
    if not ((sys.version_info.major == 3 and sys.version_info.minor >= 8) and
            (sys.version_info.major == 3 and sys.version_info.minor <= 11)):
        print("Python {}.{}.{} is not supported. You need Python 3.8 - 3.11".format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
        sys.exit(1)
    if os.path.normpath(os.getcwd()) != os.path.normpath(os.path.dirname(os.path.abspath(__file__))):
        os.chdir(os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
    launcher = importlib.import_module("src.launcher").Launcher()
    err_code = launcher.launch_bot()
    sys.exit(err_code)


if __name__ == "__main__":
    main()
