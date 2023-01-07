import shlex
import subprocess
from dataclasses import dataclass
from typing import Optional

from src.log import log


@dataclass
class ShellCommandResult:
    exit_code: int
    stdout: str
    stderr: str


class Shell:
    @staticmethod
    def run(cmd_line: str, cwd: Optional[str] = None) -> ShellCommandResult:
        cmd = shlex.split(cmd_line)
        log.debug("Executing shell command: " + cmd_line)
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        exit_code = proc.wait()
        return ShellCommandResult(exit_code, stdout.decode('utf-8'), stderr.decode('utf-8'))
