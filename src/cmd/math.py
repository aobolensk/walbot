import ast
import operator as op

from src import const
from src.commands import BaseCmd
from src.config import bc
from src.message import Msg
from src.utils import Util


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
    }

    def _evaluate_expr_node(self, node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.left), self._evaluate_expr_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.operand))
        else:
            raise Exception(f"Failed to parse '{node}'")

    def evaluate(self, expr):
        return self._evaluate_expr_node(ast.parse(expr, mode='eval').body)


class MathCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "calc",
                                     permission=const.Permission.USER.value, subcommand=True)

    @staticmethod
    async def _calc(message, command, silent=False):
        """Calculate mathematical expression
    Examples:
        !calc 2+2*2
        !calc 4/2-1"""
        if not await Util.check_args_count(message, command, silent, min=2):
            return
        expr = ' '.join(command[1:])
        try:
            ev = MathExprEvaluator()
            result = str(ev.evaluate(expr))
        except Exception as e:
            await Msg.response(message, f"Expression evaluation failed: {e}", silent)
            return
        if result is None:
            await Msg.response(message, "Unknown error happened during expression evaluation", silent)
            return
        await Msg.response(message, result, silent)
        return result
