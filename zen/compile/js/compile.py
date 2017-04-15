import zen.ast as ast
import zen.compile.js.ast as js
from zen.compile.js.environment import *


# Compile
def compile(nodes):
    env = GlobalEnvironment()
    code = [ compileExpression(node, env) for node in nodes ]
    code = [ x for e, c in code for x in c + [e] ]

    return [x for x in code if x.cls != js.Null], env


# Compile an expression
def compileExpression(node, env):
    if node.cls is ast.List:
        return compileFunctionCall(node, env)
    elif node.cls is ast.Symbol:
        env.find(node.value)
        return js.Symbol(value=node.value), []
    elif node.cls is ast.Integer:
        return js.Integer(value=node.value), []
    elif node.cls is ast.Float:
        return js.Float(value=node.value), []
    elif node.cls is ast.String:
        return js.String(value=node.value), []
    else:
        raise CompileError('Unexpected node - {}'.format(node))


# Compile a function call (i.e. evaluate an unquoted list)
def compileFunctionCall(node, env):
    from zen.compile.js.primitives import primitives
    from zen.transforms.infix import operators

    if len(node.values) == 0:
        raise CompileError('`{}` is not a function call'.format(node))
    if len(node.values) == 1:
        return compileExpression(node.values[0], env)

    f_sym = node.values[0].value

    # Check if `f` is a special form
    if f_sym in primitives:
        return primitives[f_sym](node, env)
    elif f_sym in operators:
        _, left, right = node.values

        if f_sym == '=':
            left, c1 = js.Symbol(value=left.value), []
            right, c2 = compileExpression(right, env)
        elif f_sym == '.':
            left, c1 = compileExpression(left, env)
            right, c2 = js.Symbol(value=right.value), []
        else:
            left, c1 = compileExpression(left, env)
            right, c2 = compileExpression(right, env)

        return js.Operator(op=f_sym, left=left, right=right), c1 + c2

    # If not, see if `f` is a valid symbol in the current environment
    f = env.find(f_sym)
    a = [compileExpression(expr, env) for expr in node.values[1:]]
    args = [x for x, _ in a]
    code = [x for _, c in a for x in c]

    # If everything checks out, compile into a function call
    return js.Call(f=f, args=args), code
