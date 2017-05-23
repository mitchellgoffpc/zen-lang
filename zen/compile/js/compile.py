import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.library.macros.core import *



# Compile an expression
def compileExpression(node, env):
    if node.cls is ast.List:
        return compileFunctionCall(node, env)

    elif node.cls in (ast.Symbol, ast.Operator):
        return env.find(node.value), []

    elif node.cls is ast.Boolean:
        return JSObject('bool',
            __value = js.Boolean(value=('true' if node.value else 'false')),
            __class = js.Symbol(value='bool')), []

    elif node.cls is ast.Integer:
        return JSObject('int',
            __value = js.Integer(value=node.value),
            __class = js.Symbol(value='int')), []

    elif node.cls is ast.Float:
        return JSObject('float', __value=js.Float(value=node.value)), []

    elif node.cls is ast.String:
        return JSObject('string',
            __value = js.String(value=node.value),
            __class = js.Symbol(value='str')), []

    else:
        raise CompileError('Unexpected node - {}'.format(node))



# Compile a function call (i.e. evaluate an unquoted list)
def compileFunctionCall(node, env):
    from zen.compile.js.primitives import primitives
    from zen.compile.js.macros import executeMacro

    if len(node.values) == 0:
        return JSObject('tuple', __value=js.Array(values=[]))
    if len(node.values) == 1:
        return compileExpression(node.values[0], env)

    f = node.values[0]

    # First we check if `f` is a primitive
    if f.cls in (ast.Operator, ast.Symbol) and f.value in primitives:
        return primitives[f.value](node, env)

    # Otherwise, we need to evaluate `f` and figure out what it is
    f, f_code = compileExpression(f, env)

    # If `f` is a macro, execute it straight away
    if f.cls is js.Macro:
        return executeMacro(node, env, f.macro)

    # If `f` isn't a macro, we evaluate each of the arguments and pass them to
    # `f`. However, function and method calls are handled slightly differently:
    #
    # - Methods
    #     If `f`'s first argument is a KEYWORD, then we make a METHOD call. To
    #     make one of these, we must first construct a selector from `f`'s
    #     arguments, then invoke `__dispatch_method`, which looks up the
    #     selector in `f.__methods` and calls the appropriate javascript
    #     function.
    #
    # - Functions
    #     If `f`'s first argument is NOT a KEYWORD, then we make a FUNCTION call
    #     using `__dispatch`, which simply passes the arguments to `f.__call`.

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
