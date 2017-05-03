import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.library.macros.core import *



# Compile an expression
def compileExpression(node, env):
    if node.cls is ast.List:
        return compileFunctionCall(node, env)

    elif node.cls is ast.Symbol:
        return env.find(node.value), []

    elif node.cls is ast.Boolean:
        return JSObject('bool',
            __value = js.Boolean(value=False),
            __class = js.Symbol(value='Boolean')), []

    elif node.cls is ast.Integer:
        return JSObject('int',
            __value = js.Integer(value=node.value),
            __class = js.Symbol(value='Integer')), []

    elif node.cls is ast.Float:
        return JSObject('float', __value=js.Float(value=node.value)), []

    elif node.cls is ast.String:
        return JSObject('string',
            __value = js.String(value=node.value),
            __class = js.Symbol(value='String')), []

    else:
        raise CompileError('Unexpected node - {}'.format(node))



# Compile a function call (i.e. evaluate an unquoted list)
def compileFunctionCall(node, env):
    from zen.compile.js.primitives import primitives
    from zen.compile.js.operators import operators
    from zen.compile.js.macros import executeMacro

    if len(node.values) == 0:
        return JSObject('tuple', __value=js.Array(value=[]))
    if len(node.values) == 1:
        return compileExpression(node.values[0], env)

    f = node.values[0]

    # Check if `f` is a special form
    if f.cls is ast.Operator and f.value in operators:
        return operators[f.value](node, env)
    elif f.cls is ast.Symbol:
        if f.value in primitives:
            return primitives[f.value](node, env)
        elif f.value in env.outermost().macros:
            return executeMacro(node, env, f.value)

    # If not, see if `f` is a valid symbol in the current environment
    f, f_code = compileExpression(f, env)
    method_call = isKeyword(node.values[1])

    if method_call:
        selector = js.String(value=getSelector(node.values[1:]))
        a = [compileExpression(x, env)
             for x in node.values[1:]
             if not isKeyword(x)]
    else:
        a = [compileExpression(x, env)
             for x in node.values[1:]]

    args = [x for x, _ in a]
    code = f_code + [x for _, c in a for x in c]

    if method_call:
        return js.Call(
            f = js.Symbol(value = '__dispatch_method'),
            args = [f, selector] + args), code
    else:
        return js.Call(
            f = js.Symbol(value='__dispatch'),
            args = [f] + args), code
