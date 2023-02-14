import asyncio
import os
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


@dataclass
class SSHCredentials:
    username: str
    ip: str
    password: str


class Shell:
    @staticmethod
    def run(cmd_line: str, cwd: Optional[str] = None, shell: bool = False) -> ShellCommandResult:
        log.debug("Executing shell command: " + cmd_line)
        cmd = shlex.split(cmd_line)
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)
        stdout, stderr = proc.communicate()
        return ShellCommandResult(proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    @staticmethod
    async def run_async(
            cmd_line: str, cwd: Optional[str] = None, shell: bool = False,
            timeout: int = 10) -> ShellCommandResult:
        log.debug("Executing shell command: " + cmd_line)
        cmd = shlex.split(cmd_line)
        if shell:
            proc = await asyncio.create_subprocess_shell(
                cmd_line, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            program = cmd[0]
            program_args = cmd[1:]
            proc = await asyncio.create_subprocess_exec(
                program, *program_args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            ret_code = proc.returncode
        except asyncio.exceptions.TimeoutError:
            ret_code, stdout, stderr = -1, b'', b''
        return ShellCommandResult(ret_code, stdout.decode('utf-8'), stderr.decode('utf-8'))

    @staticmethod
    async def run_ssh_async(
            cmd_line: str, ssh_credentials: SSHCredentials, *args,
            **kwargs) -> ShellCommandResult:
        os.environ["SSHPASS"] = ssh_credentials.password
        if kwargs.get("cwd", None):
            cmd_line = f"cd {kwargs['cwd']}; " + cmd_line
        cmd_line = (
            f"sshpass -e ssh -t -o StrictHostKeyChecking=no -o LogLevel=QUIET "
            f"{ssh_credentials.username}@{ssh_credentials.ip} '{cmd_line}'")
        kwargs["cwd"] = None
        try:
            return await Shell.run_async(cmd_line, *args, **kwargs)
        except Exception as e:
            raise e
        finally:
            del os.environ["SSHPASS"]

    @staticmethod
    async def run_and_send_stdout(
            execution_ctx: ExecutionContext, cmd_line: str, cwd: Optional[str] = None) -> Optional[str]:
        result = await Shell.run_async(cmd_line, cwd=cwd, shell=True)
        if result.exit_code == -1:
            await execution_ctx.send_message("<Command timed out>")
            return
        if result.exit_code != 0:
            await execution_ctx.send_message(f"<Command failed with error code {result.exit_code}>")
            return
        await execution_ctx.send_message(result.stdout)
        return result.stdout
