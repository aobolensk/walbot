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
        elif isinstance(node, ast.BinOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.left), self._evaluate_expr_node(node.right))
        elif isinstance(node, ast.BoolOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.values[0]), self._evaluate_expr_node(node.values[1]))
        elif isinstance(node, ast.UnaryOp):
            return self._ops[type(node.op)](self._evaluate_expr_node(node.operand))
        elif isinstance(node, ast.Compare):
            return int(self._ops[type(node.ops[0])](
                self._evaluate_expr_node(node.left), self._evaluate_expr_node(node.comparators[0])))
        else:
            raise Exception(f"Failed to parse '{node}'")

    def evaluate(self, expr):
        return self._evaluate_expr_node(ast.parse(expr, mode='eval').body)


class MathCommands(BaseCmd):
    def bind(self):
        bc.commands.register_command(__name__, self.get_classname(), "calc",
                                     permission=const.Permission.USER.value, subcommand=True)
        bc.commands.register_command(__name__, self.get_classname(), "if",
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
            result = str(MathExprEvaluator().evaluate(expr))
        except Exception as e:
            await Msg.response(message, f"Expression evaluation failed: {e}", silent)
            return
        await Msg.response(message, result, silent)
        return result

    @staticmethod
    async def _if(message, command, silent=False):
        """If expression is true (!= 0) then return first expression otherwise return the second one
    Examples:
        !if 1 It's true;It's false -> It's true
        !if 0 It's true;It's false -> It's false
"""
        if not await Util.check_args_count(message, command, silent, min=3):
            return
        condition = command[1]

        true = ["true"]
        false = ["false"]

        print(condition.lower(), true + false)
        if condition.lower() not in (true + false):
            condition = await Util.parse_int(
                message, command[1], f"Second parameter should be either number or {', '.join(true + false)}", silent)
            if condition is None:
                return
        else:
            # Handle keywords that can be used in conditions
            if condition.lower() in true:
                condition = 1
            elif condition.lower() in false:
                condition = 0

        expressions = ' '.join(command[2:]).split(';')
        if len(expressions) != 2:
            await Msg.response(
                message, f"There should be only 2 branches ('then' and 'else') "
                         f"separated by ';' in '{command[0]}' command", silent)
            return
        result = expressions[0] if condition != 0 else expressions[1]
        await Msg.response(message, result, silent)
        return result
