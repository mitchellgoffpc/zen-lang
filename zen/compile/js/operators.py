import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *


# def compileOperator(node, env):
#     if len(node.values) < 3:
#         raise ArgumentError('operator', len(node.values) - 1, 3, "...")
#
#     op, args, body = node.values[1], node.values[2], node.values[3:]
#     assert op.cls is ast.Operator
#     assert args.cls is ast.List
#
#     func_env = FunctionEnvironment(env, [arg.value for arg in args.values])
#     do_expr = ast.List(None, values=[ast.Symbol(None, value='do')] + body)
#
#     retexpr, code = compileExpression(do_expr, func_env)
#     body = code + [js.Return(value=retexpr)]
#     args = [js.Symbol(value=arg.value) for arg in args.values]
#
#     symbol = env.gensym()
#     env.create(op.value, symbol)
#
#     code = js.Operator(
#         op = '=',
#         left = js.Symbol(value=symbol),
#         right = JSObject('function', __call=js.Function(env=func_env, args=args, body=body)))
#
#     return js.Null(), [code]


def compileAssign(node, env):
    _, left, right = node.values
    if left.cls is ast.Symbol:
        env.create(left.value)
        left, c1 = js.Symbol(value=left.value), []
    elif (left.cls is ast.List and
          left.values[0].cls is ast.Symbol and
          left.values[0].value == 'js/dot'):
          l, c1a = compileExpression(left.values[1], env)
          r = js.Symbol(value=left.values[2].value)
          left, c1b = js.Operator(op='.', left=l, right=r), []
          c1 = c1a + c1b
    else:
        raise Exception()

    right, c2 = compileExpression(right, env)
    return js.Operator(op='=', left=left, right=right), c1 + c2


def compileDot(node, env):
    _, left, right = node.values
    left, c1 = compileExpression(left, env)
    right, c2 = js.Symbol(value=right.value), []
    return js.Operator(op='.', left=left, right=right), c1 + c2


def compileBooleanOp(node, env, op):
    _, left, right = node.values
    left, c1 = compileExpression(left, env)
    right, c2 = compileExpression(right, env)
    return JSObject('bool',
        __class = js.Symbol(value='bool'),
        __value = js.Operator(op=op, left=left, right=right)), c1 + c2
