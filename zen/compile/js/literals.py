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


# Quote compiler
def compileQuote(node, env):
    return quote(node.values[1], env)

def quote(node, env):
    if node.cls in (ast.Symbol, ast.Operator):
        return JSObject('symbol',
            __value = js.String(value=node.value)), []
    elif node.cls is ast.List:
        if (node.values and
            node.values[0].cls is ast.Symbol and
            node.values[0].value == 'unquote'):
            return compileExpression(node.values[1], env)

        else:
            quoted = [quote(x, env) for x in node.values]
            code = [x for _, c in quoted for x in c]
            values = [x for x, _ in quoted]

            return JSObject('tuple',
                __value = js.Array(
                    values = values)), code

    else:
        return compileExpression(node, env)


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
