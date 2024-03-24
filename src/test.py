import os
import shlex
import subprocess
import sys

from src import const
from src.log import log


def start_testing(args):
    if args.verbose2:
        args.verbose = True
    pytest_args = []
    pytest_args.append(sys.executable)
    pytest_args.append("-m")
    pytest_args.append("pytest")
    if args.verbose:
        pytest_args.append("-v")
    if args.verbose2:
        pytest_args.append("--capture=tee-sys")  # Capture and print stdout/stderr
    if args.cov:
        pytest_args.append("--cov")
    env = os.environ.copy()
    env["PYTHON_PATH"] = const.WALBOT_DIR
    log.debug(f"Run pytest: {shlex.join(pytest_args)}")
    ret_code = subprocess.call(pytest_args, env=env)
    return ret_code
