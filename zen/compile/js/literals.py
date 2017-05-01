import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *
from zen.library.macros.core import *


# Keyword compiler
def compileKeyword(node, env):
    assert isKeyword(node)
    return JSObject('keyword', __value=js.String(value=node.values[1].value)), []


# Map compiler
def compileMap(node, env):
    i = 1
    cells = []
    code = []

    while i < len(node.values):
        keyword = node.values[i]
        if not isKeyword(keyword):
            raise Exception("Invalid map declaration")

        name = js.String(value=keyword.values[1].value)
        value, c = compileExpression(node.values[i + 1], env)

        cells += [(name, value)]
        code += c
        i += 2

    return JSObject('map', __value=js.Object(values=cells)), code


# Lambda compiler
def compileLambda(node, env):
    if len(node.values) < 3:
        raise ArgumentError('lambda', len(node.values) - 1, 3, "...")

    args, body = node.values[1], node.values[2:]
    func_env = FunctionEnvironment(env, [arg.value for arg in args.values])
    do_expr = List(None, values=[Symbol(None, value='do')] + body)

    retexpr, code = compileExpression(do_expr, func_env)
    body = code + [js.Return(value=retexpr)]
    args = [js.Symbol(value=arg) for arg in args.values]

    return JSObject('function', __call=js.Function(env=func_env, args=args, body=body)), []
