import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.errors import *
from zen.compile.js.environment import *
from zen.compile.js.modules import *
from zen.compile.js.classes import *
from zen.compile.js.literals import *

from zen.library.macros.core import *


# Primitive compilers
def compileDo(node, env):
    exprs = [compileExpression(expr, env) for expr in node.values[1:]]
    code = [x for expr, code in exprs for x in code + [expr]]

    expr = code[-1]
    code = [x for x in code[:-1] if x.cls in (js.Return, js.Call, js.Operator, js.IfElse)]

    return expr, code


def compileVar(node, env):
    if len(node.values) == 3:
        _, name, value = node.values
    elif len(node.values) == 2:
        _, l = node.values
        if l.cls is not ast.List or len(l.values) != 3:
            raise CompileError('var must be of the form `(var {{name}} = {{value}})`')

        eq, name, value = l.values
        if eq.cls is not ast.Operator or eq.value != '=':
            raise CompileError('var must be of the form `(var {{name}} = {{value}})`')
    else:
        raise CompileError('var declaration incorrect')

    value, code = compileExpression(value, env)
    env.create(name.value)
    return js.Null(), code + [js.Operator(op='=', left=js.Symbol(value=name.value), right=value)]


def compileIf(node, env):
    symbol = env.gensym()

    _, cond, x, y = node.values
    cond, c1 = compileExpression(cond, env)
    x, c2 = compileExpression(x, env)
    y, c3 = compileExpression(y, env)

    cond = js.Operator(
        op = '.',
        left = js.Call(
            f = js.Symbol(value='__dispatch_method'),
            args = [cond, js.String(value=':bool')]),
        right = js.Symbol(value='__value'))

    code = c1 + [js.IfElse(
        cond = cond,
        x = c2 + [js.Operator(op='=', left=symbol, right=x)],
        y = c3 + [js.Operator(op='=', left=symbol, right=y)])]

    return symbol, code



# Primitive dispatch
primitives = {
    'do': compileDo,
    'var': compileVar,
    'if': compileIf,
    'map': compileMap,
    'keyword': compileKeyword,
    'lambda': compileLambda,
    'def_class': compileClass,
    'def_method': compileMethod,
    'import': compileImport }
