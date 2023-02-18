from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class ParsedArgs(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class CmdArgParser:
    @dataclass
    class ArgRule:
        arg_name: str
        cmdline_names: List[str]
        type: object
        nargs: int
        default_value: Any
        value_to_set: Any

    def __init__(self) -> None:
        self._positional_args: List[str] = []
        self._named_args: Dict[str, self.ArgRule] = {}

    def parse(self, cmd_line: List[str]) -> Optional[ParsedArgs]:
        self._args = ParsedArgs()
        for value in self._named_args.values():
            self._args[value.arg_name] = value.default_value
        positional_args_idx = 0
        for idx in range(1, len(cmd_line)):
            if positional_args_idx < len(self._positional_args):
                self._args[self._positional_args[positional_args_idx]] = cmd_line[idx]
                positional_args_idx += 1
            else:
                if cmd_line[idx] in self._named_args.keys():
                    rule = self._named_args[cmd_line[idx]]
                    if rule.value_to_set is not None:
                        self._args[rule.arg_name] = rule.value_to_set
                    elif rule.nargs == 1:
                        self._args[rule.arg_name] = cmd_line[idx + 1]
                        idx += 1
                    else:
                        raise NotImplementedError("nargs > 1 is not supported yet")
                else:
                    raise RuntimeError(f"Unknown argument '{cmd_line[idx]}'")
            idx += 1
        return self._args

    def add_positional_argument(self, name: str) -> None:
        self._positional_args.append(name)

    def add_argument(
            self, arg_name: str, cmdline_names: List[str], type: object,
            default_value: Any = None, nargs: int = 0, value_to_set: Any = None):
        if nargs > 1:
            raise NotImplementedError("nargs > 1 is not supported yet")
        if nargs != 0 and value_to_set is not None:
            raise RuntimeError(
                "Value to set should be either defined using 'value_to_set' argument or retrieved from "
                "command line using 'nargs' (number of next args to take), but not both")
        if nargs == 0 and value_to_set is None:
            raise RuntimeError(
                "Either 'nargs' or 'value_to_set' need to be provided")
        for cmdline_name in cmdline_names:
            self._named_args[cmdline_name] = self.ArgRule(
                arg_name, cmdline_name, type, nargs, default_value, value_to_set)
