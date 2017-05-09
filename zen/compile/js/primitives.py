import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.classes import *
from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.errors import *
from zen.compile.js.macros import *
from zen.compile.js.modules import *
from zen.compile.js.literals import *
from zen.compile.js.operators import *

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
    symbol = js.Symbol(value=env.gensym())

    _, cond, x, y = node.values
    cond, c1 = compileExpression(cond, env)
    x, c2 = compileExpression(x, env)
    y, c3 = compileExpression(y, env)

    cond = js.Operator(
        op = '.',
        left = js.Call(
            f = js.Symbol(value='__dispatch_method'),
            args = [cond, js.String(value=':as'), js.Symbol(value='Boolean')]),
        right = js.Symbol(value='__value'))

    code = c1 + [js.IfElse(
        cond = cond,
        x = c2 + [js.Operator(op='=', left=symbol, right=x)],
        y = c3 + [js.Operator(op='=', left=symbol, right=y)])]

    return symbol, code



def compileWhile(node, env):
    assert len(node.values) > 1

    cond, c1 = compileExpression(node.values[1], env)
    body = []

    for expr in node.values[2:]:
        e, c = compileExpression(expr, env)
        body = c + [e]

    cond = js.Operator(
        op = '.',
        left = js.Call(
            f = js.Symbol(value='__dispatch_method'),
            args = [cond, js.String(value=':bool')]),
        right = js.Symbol(value='__value'))

    code = c1 + js.While(cond=cond, body=body)

    return js.Null(), code


# Primitive dispatch
primitives = {
    'do': compileDo,
    'var': compileVar,
    'if': compileIf,
    'while': compileWhile,
    'map': compileMap,
    'quote': compileQuote,
    'keyword': compileKeyword,
    'lambda': compileLambda,
    'def-class': compileClass,
    'def-method': compileMethod,
    'def-macro': compileMacro,
    'operator': compileOperator,
    'import': compileImport,

    # operators
    '=': compileSet,
    '.': compileDot,
    'js/eq': lambda node, env: compileBooleanOp(node, env, '=='),
    'js/neq': lambda node, env: compileBooleanOp(node, env, '!=') }
