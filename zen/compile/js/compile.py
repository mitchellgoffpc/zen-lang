import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *


# Compile a Zen expression
def compileExpression(node, env):
    if node.cls is ast.List:
        return compileFunctionCall(node, env)

    elif node.cls in (ast.Symbol, ast.Operator):
        return [env.find(node.value)]

    elif node.cls is ast.Nil:
        return [JSObject(__class=js.Symbol(value='nil'))]

    elif node.cls is ast.Boolean:
        return [JSObject(
            __value = js.Boolean(value=('true' if node.value else 'false')),
            __class = env.find('Bool'))]

    elif node.cls is ast.Integer:
        return [JSObject(
            __value = js.Integer(value=node.value),
            __class = env.find('Int'))]

    elif node.cls is ast.Float:
        return [JSObject(
            __value = js.Float(value=node.value),
            __class = env.find('Float'))]

    elif node.cls is ast.String:
        return [JSObject(
            __value = js.String(value=node.value),
            __class = env.find('String'))]

    else:
        raise CompileError('Unexpected node - {}'.format(node))



# Compile a function call (i.e. an unquoted list)
def compileFunctionCall(node, env):
    from zen.compile.js.primitives import primitives
    from zen.compile.js.macros import executeMacro

    if len(node.values) == 0:
        return [JSObject(
            __value = js.Array(values=[]),
            __class = env.find('Tuple'))]
    if len(node.values) == 1:
        return compileExpression(node.values[0], env)

    f = node.values[0]

    # First we check if `f` is a primitive
    if f.cls in (ast.Operator, ast.Symbol) and f.value in primitives:
        return primitives[f.value](node, env)

    # Otherwise, we need to evaluate `f` and figure out what it is
    f_code = compileExpression(f, env)
    f = f_code.pop()

    # If `f` is a macro, execute it straight away
    if f.cls is js.Macro:
        return executeMacro(node, env, f.macro)

    # If `f` isn't a macro, we evaluate each of the arguments and pass them to
    # `f`. However, function and method calls are handled slightly differently:

    # - Methods
    #     If `f`'s first argument is a KEYWORD, then we make a METHOD call. To
    #     make one of these, we must first construct a selector from `f`'s
    #     arguments, then invoke `__dispatch_method`, which looks up the
    #     selector in `f.__methods` and calls the appropriate javascript
    #     function.

    method_call = isKeyword(node.values[1])
    code, args = [], []

    if method_call:
        selector = js.String(value=getSelector(node.values[1:]))
        keyword_args = []

        for child in node.values[1:]:
            if isKeyword(child):
                if len(keyword_args) == 1:
                    args.append(keyword_args[0])
                elif len(keyword_args) > 1:
                    args.append(JSObject(
                        __class = env.find('Array'),
                        __value = js.Array(values=keyword_args)))

                keyword_args = []

            else:
                arg_code, arg_value = compileArgument(child, env)
                code += arg_code
                keyword_args.append(arg_value)

        return f_code + code + [js.Call(
            f = js.Symbol(value = '__dispatch_method'),
            args = [f, selector] + args)]

    # - Functions
    #     If `f`'s first argument is NOT a KEYWORD, then we make a FUNCTION call
    #     using `__dispatch`, which simply passes the arguments to `f.__call` or
    #     `f.__init` if f is a Class.

    else:
        for child in node.values[1:]:
            arg_code, arg_value = compileArgument(child, env)
            code += arg_code
            args.append(arg_value)

        return f_code + code + [js.Call(
            f = js.Symbol(value='__dispatch'),
            args = [f] + args)]


# A helper function to compile a single argument to a function
def compileArgument(node, env):
    arg_code = compileExpression(node, env)
    arg_value = arg_code.pop()

    return arg_code, arg_value
