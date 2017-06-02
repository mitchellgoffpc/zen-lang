import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *


# Keyword compiler
def compileKeyword(node, env):
    assert isKeyword(node)

    value = ('nil' if node.values[1].cls is ast.Nil
                   else node.values[1].value)

    return [JSObject(
        __value = js.String(value=value),
        __class = env.find('Keyword'))]


# Regexp compiler
def compileRegexp(node, env):
    assert len(node.values) == 2
    assert node.values[1].cls is ast.String
    return [JSObject(
        __value = js.String(value=node.values[1].value),
        __class = env.find('String'))]


# Quote compiler
def compileQuote(node, env):
    return quote(node.values[1], env)

def quote(node, env):
    if node.cls in (ast.Symbol, ast.Operator):
        return [JSObject(
            __value = js.String(value=node.value),
            __class = env.find('Symbol'))]

    elif node.cls is ast.List:
        if (node.values and
            node.values[0].cls is ast.Symbol and
            node.values[0].value == 'unquote'):
            return compileExpression(node.values[1], env)

        else:
            quoted = [quote(x, env) for x in node.values]
            values = [x.pop() for x in quoted]
            code = [y for x in quoted
                      for y in x]

            return code + [JSObject(
                __value = js.Array(values=values),
                __class = env.find('Tuple'))]

    else:
        return compileExpression(node, env)
