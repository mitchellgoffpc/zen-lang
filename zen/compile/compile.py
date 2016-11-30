from zen.ast import *
from zen.compile.types import *
from zen.compile.environment import *


# Compile
def compile(nodes, env):
    main_env = FunctionEnvironment(env)
    main_env.create_arg('argc', ('INT',))
    main_env.create_arg('argv', ('POINTER', ('POINTER', ('CHAR',))))
    code = [ compileExpression(node, main_env) for node in nodes ]
    code = [ x for e, c in code for x in c + [e] ]

    return ('FUNC', main_env, 'main',
            ('INT',),
            [ ('ARG', 'argc', ('INT',)),
              ('ARG', 'argv', ('POINTER', ('POINTER', ('CHAR',)))) ],
            code)



# Compile a type
def compileType(node):
    if node.cls is List:
        return compileCompoundType(node.values)
    elif node.value == 'Int':
        return ['INT']
    elif node.value == 'Float':
        return ['FLOAT']
    else:
        raise CompileError('Unknown type - {}'.format(node.value))

def compileCompoundType(nodes):
    if nodes[0].value == 'Function':
        return ['FUNC'] + [compileType(t) for t in nodes[1:]]
    elif nodes[0].value == 'Pointer':
        return ['POINTER'] + compileType(nodes[1])
    else:
        raise CompileError('Unknown type - {}'.format(nodes[0].value))



# Compile an expression
def compileExpression(node, env):
    if node.cls is List:
        return compileFunctionCall(node, env)
    elif node.cls is Symbol:
        env.find(node.value)
        return ('SYMBOL', node.value), []
    elif node.cls is Integer:
        return ('INT', node.value), []
    elif node.cls is Float:
        return ('FLOAT', node.value), []
    else:
        raise CompileError('Unexpected node - {}'.format(node))


# Compile a function call (i.e. evaluate an unquoted list)
def compileFunctionCall(node, env):
    from zen.compile.primitives import primitives
    from zen.compile.primitives import operators

    if node.cls is not List or len(node.values) == 0:
        raise CompileError('`{}` is not a function call'.format(node))

    f_sym = node.values[0].value

    # Check if `f` is a special form
    if f_sym in primitives:
        return primitives[f_sym](node, env)
    elif f_sym in operators:
        _, left, right = node.values
        left, c1 = compileExpression(left, env)
        right, c2 = compileExpression(right, env)
        return ('OPERATOR', f_sym, left, right), c1 + c2

    # If not, match `f`'s type signiture against `type`
    f = env.find(f_sym)
    a = [compileExpression(expr, env) for expr in node.values[1:]]
    args = [(x, []) for x, _ in a]
    code = [x for _, c in a for x in c]

    # If everything checks out, compile into a function call
    return ('CALL', f_sym, args), code
