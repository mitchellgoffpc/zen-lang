import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.unpackers import *
from zen.compile.js.util import *

from zen.library.macros.core import *


# `lambda` compiler

# A lambda is a CONDITIONAL FUNCTION. Like any other function, it can set
# requirements that its arguments must meet, and if these requirements
# aren't met, the function will throw an error.

def compileLambda(node, env):
    if len(node.values) < 3:
        raise ArgumentError('lambda', len(node.values) - 1, 3, "...")

    args, body = node.values[1], node.values[2:]
    assert args.cls is ast.List

    cf = compileConditionalFunction(env, args.values, body)
    return JSObject('function', __call=cf), []


# `def` compiler

# `def` statements can stack on top of each other, allowing the CONDITIONAL
# FUNCTION to test MANY different conditionals and select the first one whose
# conditions are met. When the compiler encounters a `def` statement, it
# assigns it a special label in the environment so it can be found again later.
# When we write another `def` statement later on, the compiler checks if the
# given name already has a label in the environment; if so, we append
# the conditional from the NEW `def` to the EXISTING conditional
# function.

def compileFunction(node, env):
    name, args, body = node.values[1], node.values[2], node.values[3:]
    assert name.cls is ast.Symbol
    assert args.cls is ast.List

    if name.value in env.labels:
        cf = env.labels[name.value]
        cond = compileConditional(FunctionEnvironment, cf.env, args.values, body)
        cf.conditionals.append(cond)
        code = []

    else:
        cf = compileConditionalFunction(FunctionEnvironment, env, args.values, body)
        symbol = env.create(name.value)
        env.labels[name.value] = cf
        code = [js.Operator(
            op = '=',
            left = js.Symbol(value=symbol),
            right = JSObject('function', __call=cf))]

    return js.Null(), code



# `operator` compiler

def compileOperator(node, env):
    if len(node.values) < 3:
        raise ArgumentError('operator', len(node.values) - 1, 3, "...")

    op, args, body = node.values[1], node.values[2], node.values[3:]
    assert op.cls is ast.Operator
    assert args.cls is ast.List

    if op.value in env.labels:
        cf = env.labels[op.value]
        cond = compileConditional(FunctionEnvironment, cf.env, args.values, body)
        cf.conditionals.append(cond)
        code = []

    else:
        cf = compileConditionalFunction(FunctionEnvironment, env, args.values, body)
        symbol = env.create(op.value)
        env.labels[op.value] = cf

        code = [js.Operator(
            op = '=',
            left = js.Symbol(value=symbol),
            right = JSObject('function', __call=cf))]

    return js.Null(), code



# `init` compiler

def compileInit(node, env):
    assert node.cls is List
    assert len(node.values) >= 3
    assert node.values[1].cls is List

    args, body = node.values[1], node.values[2:]

    if env.init:
        cf = env.init
        cond = compileConditional(InitEnvironment, cf.env, args.values, body, len(cf.args))
        cf.conditionals.append(cond)

    else:
        env.init = compileConditionalFunction(
            InitEnvironment, env, args.values, body, ['_self'])

    return JSObject('function', __call=env.init)



# `def-method` compiler

def compileMethod(node, env):
    assert node.cls is List
    assert len(node.values) >= 3
    assert node.values[1].cls is List
    assert len(node.values[1].values) > 0

    args, body = node.values[1], node.values[2:]

    selector = ''.join(
        ':{}'.format(arg.values[1].value)
        for arg in args.values
        if isKeyword(arg))

    args = [arg for arg in args.values
                if not isKeyword(arg)]

    if selector in env.labels:
        cf = env.labels[selector]
        cond = compileConditional(MethodEnvironment, cf.env, args, body, len(cf.args))
        cf.conditionals.append(cond)
        return None

    else:
        cf = compileConditionalFunction(
            MethodEnvironment, env, args, body, ['_self'])
        env.labels[selector] = cf
        return (js.String(value=selector), cf)



# Creates a conditional function.
def compileConditionalFunction(EnvCls, env, args, body, function_args = []):
    dummy_env = FunctionEnvironment(env)
    conditional = compileConditional(EnvCls, dummy_env, args, body, len(function_args))

    return js.ConditionalFunction(
        env = dummy_env,
        args = [js.Symbol(value=x) for x in function_args],
        conditionals = [conditional])


def compileConditional(EnvCls, env, args, body, start = 0):
    assert env.__class__ is not ClassEnvironment

    unpackers = getUnpackers(args, start)
    source = 'js/arguments'

    symbols = [x.symbol(env) for x in unpackers]
    cond_env = EnvCls(env, {x:y for x, y in symbols})
    conditions = [x.compileCondition(env, source) for x in unpackers]
    unpacked = [y for x in unpackers
                  for y in x.compileUnpack(cond_env, source)]

    # Compile the body
    do_expr = ast.List(None, values=[ast.Symbol(None, value='do')] + body)
    retexpr, code = compileExpression(do_expr, cond_env)
    body = unpacked + code + [js.Return(value=retexpr)]

    return js.Conditional(
        env = cond_env,
        test = joinConditions(conditions),
        body = body)



# Helper functions
def getUnpackers(args, start):
    unpackers = []
    i = 0

    if (len(args) == 3 and
        args[0].cls is ast.Operator and
        args[0].value == '|'):
        return [TypeUnpacker(start, args[1], args[2])]

    while i < len(args):
        arg = args[i]

        if (arg.cls is ast.Operator and
            arg.value == '&'):
            i += 1
            arg = args[i]
            unpackers.append(RemainingUnpacker(i, arg))

        elif arg.cls is ast.Symbol:
            unpackers.append(DefaultUnpacker(i, arg))

        elif arg.cls in (ast.Integer, ast.String):
            value = compileExpression(arg, env)
            unpackers.append(LiteralUnpacker(i, value))

        elif arg.cls is ast.List:
            if (len(arg.values) == 3 and
                arg.values[0].cls is ast.Operator and
                arg.values[0].value == '|'):
                unpackers.append(TypeUnpacker(i, arg.values[1], arg.values[2]))

            else:
                raise Exception("Unpacking tuples hasn't been implemented yet!")

        i += 1

    return unpackers


def joinConditions(conditions):
    if len(conditions) == 0:
        return js.Boolean(value=True)
    else:
        return js.Operator(
            op = '&&',
            left = conditions[0],
            right = joinConditions(conditions[1:]))
