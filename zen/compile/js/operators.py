import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *


def compileSet(node, env):
    _, left, right = node.values
    left, c1 = js.Symbol(value=left.value), []
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
        __class = js.Symbol(value='Boolean'),
        __value = js.Operator(
            op = op,
            left = js.Operator(op='.', left=left, right=js.Symbol(value='__value')),
            right = js.Operator(op='.', left=right, right=js.Symbol(value='__value')))), c1 + c2



# Operator dispatch
operators = {
    '=': compileSet,
    '.': compileDot,
    '==': lambda node, env: compileBooleanOp(node, env, '==') }
