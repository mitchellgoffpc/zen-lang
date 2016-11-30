from zen.compile.compile import *
from zen.compile.environment import *
from zen.compile.errors import *


# Primitive compilers
def compileSet(node, env):
    _, cell, value = node.values
    name, type = cell.key, cell.value

    type = compileType(type)
    value, code = compileExpression(value, env)

    env.create(name.value, type)
    return ('ASSIGN', name.value, value), code



def compileDo(node, env):
    code = [compileExpression(expr, env) for expr in node.values[2:-1]]
    ret_expr = compileExpression(node.values[-1], env)

    return ret_expr, code



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
    if len(node.values) != 4:
        raise ArgumentError('lambda', len(node.values) - 1, 3, 3)

    _, type, args, body = node.values

    outermost = env.outermost()
    func_name = outermost.gen()
    ret_type = compileType(type)

    args = { cell.key.value: compileType(cell.value) for cell in args.values }
    func_type = ('FUNC', ret_type, args.values())
    func_env = FunctionEnvironment(outermost, args)
    func_args = [('ARG', s, t) for s, t in args.items()]

    retexpr, code = compileExpression(body, func_env)
    body = code + [('RETURN', retexpr)]

    outermost.assign(func_name, func_type,
        ('FUNC', func_env, func_name, ret_type, func_args, body))

    return ('SYMBOL', func_name), []



# Primitive dispatch
primitives = {
    'set': compileSet,
    'do': compileDo,
    'lambda': compileLambda,
    'if': compileIf }

operators = ['+', '-', '*', '/', '&&', '||']
