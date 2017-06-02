import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.classes import *
from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.errors import *
from zen.compile.js.functions import *
from zen.compile.js.imports import *
from zen.compile.js.macros import *
from zen.compile.js.modules import *
from zen.compile.js.literals import *
from zen.compile.js.operators import *


# Compile a (do ...) expression
def compileDo(node, env):
    return [x for expr in node.values[1:]
              for x in compileExpression(expr, env)]


# Compile a (js/if-else ...) expression
def compileIfElse(node, env):
    symbol = env.gensym()

    _, cond, x, y = node.values
    c1 = compileExpression(cond, env)
    c2 = compileExpression(x, env)
    c3 = compileExpression(y, env)
    cond, x, y = c1.pop(), c2.pop(), c3.pop()

    return c1 + [
        js.Var(value=symbol.value),
        js.IfElse(
            cond = cond,
            x = c2 + [js.Operator(op='=', left=symbol, right=x)],
            y = c3 + [js.Operator(op='=', left=symbol, right=y)]),
        symbol]


# Forward-declare a symbol
def compileDeclare(node, env):
    for child in node.values[1:]:
        assert  child.cls is ast.Symbol
        try:    env.find(child.value)
        except: env.create(child.value)
    return []


# Compile a (comment ...) expression. This is just a stub for now.
def compileComment(node, env):
    return []


# This is a dispatcher which maps all of the the primitive Zen functions to
# their respective Python compiler functions.
primitives = {
    'do': compileDo,
    'declare': compileDeclare,
    'import': compileImport,
    'comment': compileComment,
    'js/if-else': compileIfElse,

    'regexp': compileRegexp,
    'quote': compileQuote,
    'keyword': compileKeyword,

    'lambda': compileLambda,
    'def': compileFunction,
    'class': compileClass,
    'extend': compileExtend,
    'def-method': compileMethod,
    'def-macro': compileMacro,
    'def-operator': compileFunction,

    # operators
    'js/dot': compileDot,
    'js/assign': compileAssign,

    'js/eq':  lambda node, env: compileOp(node, env, '==', 'Bool'),
    'js/neq': lambda node, env: compileOp(node, env, '!=', 'Bool'),
    'js/and': lambda node, env: compileOp(node, env, '&&', 'Bool'),
    'js/or':  lambda node, env: compileOp(node, env, '||', 'Bool'),

    'js/add': lambda node, env: compileOp(node, env, '+', 'Int'),
    'js/sub': lambda node, env: compileOp(node, env, '-', 'Int'),
    'js/mul': lambda node, env: compileOp(node, env, '*', 'Int'),
    'js/div': lambda node, env: compileOp(node, env, '/', 'Int')}
