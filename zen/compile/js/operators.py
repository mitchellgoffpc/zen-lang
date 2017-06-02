import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *


def compileAssign(node, env):
    _, left, right = node.values
    if left.cls is ast.Symbol:
        symbol = env.create(left.value)
        left, c1 = js.Symbol(value=symbol), []

    elif (left.cls is ast.List and
          left.values[0].cls is ast.Symbol and
          left.values[0].value == 'js/dot'):

          c1 = compileExpression(left.values[1], env)
          l = c1.pop()
          r = js.Symbol(value=left.values[2].value)
          left = js.Operator(op='.', left=l, right=r)

    else:
        raise Exception()

    c2 = compileExpression(right, env)
    right = c2.pop()

    return c1 + c2 + [js.Operator(op='=', left=left, right=right)]


def compileDot(node, env):
    _, left, right = node.values
    code = compileExpression(left, env)
    left = code.pop()
    right = js.Symbol(value=right.value)
    return code + [js.Operator(op='.', left=left, right=right)]


def compileOp(node, env, op, cls):
    _, left, right = node.values
    c1 = compileExpression(left, env)
    c2 = compileExpression(right, env)
    left, right = c1.pop(), c2.pop()

    return c1 + c2 + [JSObject(
        __class = env.find(cls),
        __value = js.Operator(op=op, left=left, right=right))]
