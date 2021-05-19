import os
import subprocess
import sys


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
    subprocess.call(
        pytest_args,
        env={
            "PYTHON_PATH": os.getcwd()
        },
    )
