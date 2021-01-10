import os
import subprocess
import sys


def start_testing():
    subprocess.call(
        [sys.executable, "-m", "pytest"],
        env={
            "PYTHON_PATH": os.getcwd()
        },
        )
