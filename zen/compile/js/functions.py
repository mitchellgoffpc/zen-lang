import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.unpackers import *
from zen.compile.js.util import *


# A `lambda` is a CONDITIONAL FUNCTION, which means it can place restrictions
# on the values and types of its arguments. meet. If these conditions aren't
# met, the function will throw an error.

def compileLambda(node, env):
    if len(node.values) < 3:
        raise ArgumentError('lambda', len(node.values) - 1, 3, "...")

    args, body = node.values[1], node.values[2:]
    assert args.cls is ast.List

    cf = compileConditionalFunction(FunctionEnvironment, env, args.values, body)
    return [JSObject(
        __call = cf,
        __class = env.find('Function'))]


# `def` compiler

# `def` statements can stack on top of each other, allowing the CONDITIONAL
# FUNCTION to test MANY different conditionals and dispatch the first one whose
# conditions are met. When the compiler encounters a `def` statement, it
# attaches the function's contents to its symbol so it can be found again later.
# When we `def` another function later on, the Zen compiler checks if any
# functions with that name are already defined; if so, it appends the
# conditional from the NEW `def` to the EXISTING conditiona function.

def compileFunction(node, env):
    name, args, body = node.values[1], node.values[2], node.values[3:]
    assert name.cls in (ast.Symbol, ast.Operator)
    assert args.cls is ast.List

    try:
        symbol = env.find(name.value)
        cf = symbol.contents
        cond = compileConditional(FunctionEnvironment, cf.env, args.values, body)
        cf.conditionals.append(cond)
        return []

    except ReferenceError:
        cf = compileConditionalFunction(FunctionEnvironment, env, args.values, body)
        symbol = env.create(name.value)
        symbol.contents = cf
        return [js.Operator(
            op = '=',
            left = symbol,
            right = JSObject(
                __call = cf,
                __class = env.find('Function')))]


# `init` compiler

def compileInit(node, env):
    assert node.cls is ast.List
    assert len(node.values) >= 3
    assert node.values[1].cls is ast.List

    args, body = node.values[1], node.values[2:]

    return compileConditional(InitEnvironment, env, args.values, body, 1)


# `def-method` compiler

def compileMethod(node, env):
    assert node.cls is ast.List
    assert len(node.values) >= 3
    assert node.values[1].cls is ast.List
    assert len(node.values[1].values) > 0

    args, body = node.values[1], node.values[2:]

    selector = ''.join(
        ':{}'.format(arg.values[1].value)
        for arg in args.values
        if isKeyword(arg))

    args = [arg for arg in args.values
                if not isKeyword(arg)]

    cf = compileConditionalFunction(
        MethodEnvironment, env, args, body, ['_self'])
    return js.String(value=selector), cf



# Creates a conditional function.
def compileConditionalFunction(EnvCls, env, args, body, function_args = []):
    dummy_env = FunctionEnvironment(env)
    conditional = compileConditional(EnvCls, dummy_env, args, body, len(function_args))

    return js.ConditionalFunction(
        env = dummy_env,
        args = [js.Symbol(value=x) for x in function_args],
        conditionals = [conditional])


def compileConditional(EnvCls, env, args, body, start = 0):
    unpackers = getUnpackers(args, start)
    source = 'js/arguments'

    cond_env = EnvCls(env)
    conditions = [x.compileCondition(env, source) for x in unpackers]
    unpacked = [y for x in unpackers
                  for y in x.compileUnpack(cond_env, source)]

    # Compile the body
    code = [x for expr in body
              for x in compileExpression(expr, cond_env)]
    value = code.pop()

    return js.Conditional(
        env = cond_env,
        test = joinConditions(conditions),
        body = unpacked + code + [js.Return(value=value)])



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
