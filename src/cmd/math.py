import ast
import operator as op
from typing import List, Optional

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import Util, null


class MathExprEvaluator:
    def _limited_power(a, b):
        if b > 100:
            raise ValueError(f"Exponent {b} is too big")
        return op.pow(a, b)

    _ops = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: _limited_power,
        ast.FloorDiv: op.floordiv,
        ast.Mod: op.mod,
        ast.BitAnd: op.and_,
        ast.BitOr: op.or_,
        ast.BitXor: op.xor,
        ast.Invert: op.inv,
        ast.LShift: op.lshift,
        ast.RShift: op.rshift,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
        ast.Eq: op.eq,
        ast.NotEq: op.ne,
        ast.Lt: op.lt,
        ast.LtE: op.le,
        ast.Gt: op.gt,
        ast.GtE: op.ge,
        ast.And: op.and_,
        ast.Or: op.or_,
    }

    def _evaluate_expr_node(self, node):
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.left), self._evaluate_expr_node(node.right))
        if isinstance(node, ast.BoolOp):
            return self._ops[type(node.op)](
                self._evaluate_expr_node(node.values[0]), self._evaluate_expr_node(node.values[1]))
        if isinstance(node, ast.UnaryOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.operand))
        if isinstance(node, ast.Compare):
            return int(self._ops[type(node.ops[0])](
                self._evaluate_expr_node(node.left), self._evaluate_expr_node(node.comparators[0])))
        raise Exception(f"Failed to parse '{node}'")

    def evaluate(self, expr):
        return self._evaluate_expr_node(ast.parse(expr, mode='eval').body)


class MathCommands(BaseCmd):
    def bind(self) -> None:
        bc.executor.commands["calc"] = Command(
            "math", "calc", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._calc)
        bc.executor.commands["if"] = Command(
            "math", "if", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._if)
        bc.executor.commands["loop"] = Command(
            "math", "loop", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._loop)

    async def _calc(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Calculate mathematical expression
    Examples:
        !calc 2+2*2
        !calc 4/2-1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return None
        expr = ' '.join(cmd_line[1:])
        try:
            result = str(MathExprEvaluator().evaluate(expr))
        except Exception as e:
            return null(await Command.send_message(execution_ctx, f"Expression evaluation failed: {e}"))
        await Command.send_message(execution_ctx, result)
        return result

    async def _if(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """If expression is true (!= 0) then return first expression otherwise return the second one
    Examples:
        !if 1 It's true;It's false -> It's true
        !if 0 It's true;It's false -> It's false
"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return None
        condition = cmd_line[1]

        true = ["true"]
        false = ["false"]

        if condition.lower() not in true + false:
            condition = await Util.parse_int(
                execution_ctx, cmd_line[1], f"Second parameter should be either number or {', '.join(true + false)}")
            if condition is None:
                return None
        else:
            # Handle keywords that can be used in conditions
            if condition.lower() in true:
                condition = 1
            elif condition.lower() in false:
                condition = 0

        expressions = ' '.join(cmd_line[2:]).split(';')
        if len(expressions) != 2:
            return null(
                await Command.send_message(
                    execution_ctx,
                    f"There should be only 2 branches ('then' and 'else') "
                    f"separated by ';' in '{cmd_line[0]}' command"))
        result = expressions[0] if condition != 0 else expressions[1]
        await Command.send_message(execution_ctx, result)
        return result

    async def _loop(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> Optional[str]:
        """Repeat an action n times
    Examples:
        !loop 2 ping
        !loop 5 echo Hello!"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=3):
            return None
        subcommand = cmd_line[2:]
        loop_count = await Util.parse_int(
            execution_ctx, cmd_line[1], "Loop iterations count should be an integer")
        if loop_count is None:
            return None
        if loop_count <= 0:
            await Command.send_message(execution_ctx, "Loop iterations count should be greater than 0")
        result = ""
        silent_state = execution_ctx.silent
        execution_ctx.silent = True
        try:
            for _ in range(loop_count):
                result += await bc.executor.commands[subcommand[0]].run(subcommand, execution_ctx) + ' '
        except KeyError:
            execution_ctx.silent = silent_state
            await Command.send_message(execution_ctx, f"Unknown command '{subcommand[0]}'")
        else:
            execution_ctx.silent = silent_state
        await Command.send_message(execution_ctx, result)
        return result
