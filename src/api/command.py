import enum
from abc import abstractmethod
from types import FunctionType
from typing import Any, Dict, List

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
        self.times_called = 0
        if impl_type == Implementation.FUNCTION:
            self._exec = impl_func
            self.description = self._exec.__doc__
        elif impl_type == Implementation.MESSAGE:
            self.impl_message = impl_message
            self.description = impl_message
        else:
            raise NotImplementedError(f"Implementation type {impl_type} is not supported")

    def load_persistent_state(self, commands_data: Dict[str, Any]):
        if self.command_name not in commands_data.keys():
            return
        state = commands_data[self.command_name]
        if "permission_level" in state.keys():
            self.permission_level = const.Permission(state["permission_level"])
        if "times_called" in state.keys():
            self.times_called = state["times_called"]

    def store_persistent_state(self, commands_data: Dict[str, Any]):
        if self.command_name not in commands_data.keys():
            commands_data[self.command_name] = dict()
        commands_data[self.command_name]["permission_level"] = int(self.permission_level)
        commands_data[self.command_name]["times_called"] = self.times_called

    def run(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> None:
        if execution_ctx.platform != "discord":
            # On Discord platform we are using legacy separate permission handling or now
            if execution_ctx.permission_level < self.permission_level:
                self.send_message(execution_ctx, f"You don't have permission to call command '{cmd_line[0]}'")
                return
        self.times_called += 1
        if self.impl_type == Implementation.FUNCTION:
            return self._exec(cmd_line, execution_ctx)
        elif self.impl_type == Implementation.MESSAGE:
            result = self.process_variables(execution_ctx, self.impl_message, cmd_line)
            result = self._process_message(result)
            return execution_ctx.send_message(result)

    def _process_message(self, message: str) -> str:
        return message

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

    @staticmethod
    def process_variables(execution_ctx: ExecutionContext, string: str, cmd_line: List[str], safe=False) -> str:
        if execution_ctx.platform == "discord":
            string = string.replace("@author@", execution_ctx.message.author.mention)
            string = string.replace("@channel@", execution_ctx.message.channel.mention)
            string = string.replace("@server@", execution_ctx.message.guild.name)
            string = string.replace("@authorid@", str(execution_ctx.message.author.id))
        string = string.replace("@command@", ' '.join(cmd_line))
        if not safe or const.ALNUM_STRING_REGEX.match(' '.join(cmd_line[1:])):
            string = string.replace("@args@", ' '.join(cmd_line[1:]))
            it = 0
            while True:
                res = const.ARGS_REGEX.search(string[it:])
                if res is None:
                    break
                n1 = 1
                n2 = len(cmd_line)
                if res.group(1):
                    n1 = int(res.group(1))
                if res.group(2):
                    n2 = int(res.group(2)) + 1
                if not 0 < n1 < len(cmd_line) or not 0 < n2 <= len(cmd_line) or n1 > n2:
                    it += res.end()
                    continue
                oldlen = len(string)
                if not safe or const.ALNUM_STRING_REGEX.match(' '.join(cmd_line[n1:n2])):
                    string = string.replace(res.group(0), ' '.join(cmd_line[n1:n2]), 1)
                it += res.end() + len(string) - oldlen
        for i in range(len(cmd_line)):
            if not safe or const.ALNUM_STRING_REGEX.match(cmd_line[i]):
                string = string.replace("@arg" + str(i) + "@", cmd_line[i])
        return string


class Executor:
    def __init__(self) -> None:
        self.commands = {}

    def add_module(self, module: BaseCmd) -> None:
        module.bind()

    def load_persistent_state(self, commands_data: Dict[str, Any]):
        for command in self.commands.values():
            command.load_persistent_state(commands_data)

    def store_persistent_state(self, commands_data: Dict[str, Any]):
        for command in self.commands.values():
            command.store_persistent_state(commands_data)
