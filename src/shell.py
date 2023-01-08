import asyncio
import shlex
import subprocess
from dataclasses import dataclass
from typing import Optional

from src.api.execution_context import ExecutionContext
from src.log import log


@dataclass
class ShellCommandResult:
    exit_code: int
    stdout: str
    stderr: str


class Shell:
    @staticmethod
    def run(cmd_line: str, cwd: Optional[str] = None, shell: bool = False) -> ShellCommandResult:
        cmd = shlex.split(cmd_line)
        log.debug("Executing shell command: " + cmd_line)
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        stdout, stderr = proc.communicate()
        return ShellCommandResult(proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    async def run_async(cmd_line: str, cwd: Optional[str] = None, shell: bool = False) -> ShellCommandResult:
        cmd = shlex.split(cmd_line)
        if shell:
            proc = await asyncio.create_subprocess_shell(
                cmd_line, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            program = cmd[0]
            program_args = cmd[1:]
            proc = await asyncio.create_subprocess_exec(
                program, *program_args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        return ShellCommandResult(proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    async def run_and_send_stdout(
            execution_ctx: ExecutionContext, cmd_line: str, cwd: Optional[str] = None) -> Optional[str]:
        result = await Shell.run_async(cmd_line, cwd=cwd, shell=True)
        if result.exit_code != 0:
            await execution_ctx.send_message(f"<Command failed with error code {result.exit_code}>")
            return
        await execution_ctx.send_message(result.stdout)
        return result.stdout
