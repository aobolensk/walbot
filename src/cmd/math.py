import ast
import operator as op
from typing import List

from src import const
from src.api.command import BaseCmd, Command, Implementation
from src.api.execution_context import ExecutionContext
from src.config import bc
from src.utils import null


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
    def __init__(self) -> None:
        pass
    def bind(self) -> None:
        bc.executor.commands["calc"] = Command(
            "math", "calc", const.Permission.USER, Implementation.FUNCTION,
            subcommand=True, impl_func=self._calc)

    async def _calc(self, cmd_line: List[str], execution_ctx: ExecutionContext) -> str:
        """Calculate mathematical expression
    Examples:
        !calc 2+2*2
        !calc 4/2-1"""
        if not await Command.check_args_count(execution_ctx, cmd_line, min=2):
            return
        expr = ' '.join(cmd_line[1:])
        try:
            result = str(MathExprEvaluator().evaluate(expr))
        except Exception as e:
            return null(await Command.send_message(execution_ctx, f"Expression evaluation failed: {e}"))
        await Command.send_message(execution_ctx, result)
        return result
