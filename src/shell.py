import asyncio
import shlex
import subprocess
from dataclasses import dataclass
from typing import Dict, Optional

from src.api.execution_context import ExecutionContext
from src.log import log


@dataclass
class ShellCommandResult:
    """Result of a shell command execution."""

    exit_code: int
    stdout: str
    stderr: str


@dataclass
class SSHCredentials:
    """Simple holder for SSH connection credentials."""

    username: str
    ip: str
    password: str


class Shell:
    @staticmethod
    def run(cmd_line: str, cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None, shell: bool = False) -> ShellCommandResult:
        """Run shell command synchronously and return its result."""
        log.debug("Executing shell command: " + cmd_line)
        if shell:
            proc = subprocess.Popen(
                cmd_line,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
        else:
            cmd = shlex.split(cmd_line)
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
            )
        stdout, stderr = proc.communicate()
        return ShellCommandResult(proc.returncode, stdout.decode('utf-8'), stderr.decode('utf-8'))

    @staticmethod
    async def run_async(
            cmd_line: str, cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None,
            shell: bool = False,
            timeout: int = 10) -> ShellCommandResult:
        """Run shell command asynchronously with optional timeout.

        If the timeout is exceeded, the spawned process is killed and
        awaited before returning.
        """
        log.debug("Executing shell command: " + cmd_line)
        if shell:
            proc = await asyncio.create_subprocess_shell(
                cmd_line,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            cmd = shlex.split(cmd_line)
            program, _ = cmd
            proc = await asyncio.create_subprocess_exec(
                program,
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            ret_code = proc.returncode
        except asyncio.exceptions.TimeoutError:
            proc.kill()
            await proc.wait()
            ret_code, stdout, stderr = -1, b'', b''
        return ShellCommandResult(ret_code, stdout.decode('utf-8'), stderr.decode('utf-8'))

    @staticmethod
    async def run_ssh_async(
            cmd_line: str, ssh_credentials: SSHCredentials, *args,
            **kwargs) -> ShellCommandResult:
        """Run command on a remote host via SSH."""
        if kwargs.get("cwd", None):
            cmd_line = f"cd {kwargs['cwd']}; " + cmd_line
        cmd_line = (
            f"sshpass -e ssh -t -o StrictHostKeyChecking=no -o LogLevel=QUIET "
            f"{ssh_credentials.username}@{ssh_credentials.ip} '{cmd_line}'")
        kwargs["cwd"] = None
        try:
            return await Shell.run_async(cmd_line, env={"SSHPASS": ssh_credentials.password}, *args, **kwargs)
        except Exception as e:
            raise e

    @staticmethod
    async def run_and_send_stdout(
            execution_ctx: ExecutionContext, cmd_line: str, cwd: Optional[str] = None) -> Optional[str]:
        """Run command, send stdout to chat and return it."""
        result = await Shell.run_async(cmd_line, cwd=cwd, shell=True)
        if result.exit_code == -1:
            await execution_ctx.send_message("<Command timed out>")
            return None
        if result.exit_code != 0:
            await execution_ctx.send_message(f"<Command failed with error code {result.exit_code}>")
            return None
        await execution_ctx.send_message(result.stdout)
        return result.stdout
