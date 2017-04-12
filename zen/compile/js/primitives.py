import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.errors import *


# Primitive compilers
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



def compileDo(node, env):
    exprs = [compileExpression(expr, env) for expr in node.values[1:]]
    code = [x for expr, code in exprs for x in code + [expr]]
            
    expr = code[-1]
    code = [x for x in code[:-1] if x.cls in (js.Return, js.Call, js.Operator)]
    return expr, code



def compileIf(node, env):
    if len(node.values) in [4, 5]:
        _, type, cond, then = node.values[:4]

        ret_sym = env.gen()
        type = compileType(type)
        cond, code = compileExpression(cond, env)

        then, c1 = compileExpression(then, env)
        then = c1 + [('ASSIGN', ret_sym, then)]

        env.create(ret_sym, type)
    else:
        raise ArgumentError('if', len(node.values) - 1, 3, 4)

    if len(node.values) == 4:
        alt = [('ASSIGN', ret_sym, 'NIL')]
    elif len(node.values) == 5:
        alt, c2 = compileExpression(node.values[4], env)
        alt = c2 + [('ASSIGN', ret_sym, alt)]

    return ('SYMBOL', ret_sym), code + [('IF-ELSE', cond, then, alt)]



def compileLambda(node, env):
    if len(node.values) != 3:
        raise ArgumentError('lambda', len(node.values) - 1, 2, 2)

    _, args, body = node.values

    func_env = FunctionEnvironment(env, [arg.value for arg in args.values])
    retexpr, code = compileExpression(body, func_env)
    body = code + [js.Return(value=retexpr)]
    args = [js.Symbol(value=arg) for arg in args.values]

    return js.Function(env=func_env, args=args, body=body), []




# Literal compilers
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

    return js.Object(values=cells), code



# Helper functions
def isKeyword(node):
    return (
        node.cls is ast.List and
        len(node.values) == 2 and
        node.values[0].cls is ast.Symbol and
        node.values[0].value == 'keyword' and
        node.values[1].cls is ast.Symbol)



# Primitive dispatch
primitives = {
    'var': compileVar,
    'do': compileDo,
    'lambda': compileLambda,
    'map': compileMap }
