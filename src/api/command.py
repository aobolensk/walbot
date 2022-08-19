import enum
from abc import abstractmethod
from types import FunctionType
from typing import List

from src import const


class BaseCmd:
    @classmethod
    def get_classname(cls) -> str:
        return cls.__name__

    def bind(self) -> None:
        raise NotImplementedError(f"Class {self.get_classname()} does not have bind() function")


class ExecutionContext:
    def __init__(self) -> None:
        self.platform = "<unknown>"
        self.permission_level = const.Permission.USER

    @abstractmethod
    def send_message(self, message: str, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def disable_pings(self, message: str) -> None:
        pass


class Implementation(enum.IntEnum):
    FUNCTION = 0
    MESSAGE = 1


class Command:
    def __init__(
            self, module_name: str, command_name: str, permission_level: const.Permission,
            impl_type: Implementation, subcommand: bool = False,
            impl_func: FunctionType = None, impl_message: str = None) -> None:
        self.module_name = module_name
        self.command_name = command_name
        self.permission_level = permission_level
        self.subcommand = subcommand
        self.impl_type = impl_type
        if impl_type == Implementation.FUNCTION:
            self._exec = impl_func
            self.description = self._exec.__doc__
        elif impl_type == Implementation.MESSAGE:
            self._exec = impl_message
            self.description = impl_message
        else:
            raise NotImplementedError(f"Implementation type {impl_type} is not supported")

    def run(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if execution_ctx.platform != "discord":
            # On Discord platform we are using legacy separate permission handling or now
            if execution_ctx.permission_level < self.permission_level:
                self.send_message(execution_ctx, f"You don't have permission to call command '{cmd_line[0]}'")
        if self.impl_type == Implementation.FUNCTION:
            return self._exec(cmd_line, execution_ctx)
        elif self.impl_type == Implementation.MESSAGE:
            return self.impl_message

    @abstractmethod
    def _exec(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> str:
        pass

    @staticmethod
    def check_args_count(execution_ctx, cmd_line, min=None, max=None):
        if min and len(cmd_line) < min:
            Command.send_message(execution_ctx, f"Too few arguments for command '{cmd_line[0]}'")
            return False
        if max and len(cmd_line) > max:
            Command.send_message(execution_ctx, f"Too many arguments for command '{cmd_line[0]}'")
            return False
        return True

    @staticmethod
    def send_message(execution_ctx: ExecutionContext, message: str) -> None:
        execution_ctx.send_message(message)


class Executor:
    def __init__(self) -> None:
        self.commands = {}

    def add_module(self, module: BaseCmd) -> None:
        module.bind(self.commands)
