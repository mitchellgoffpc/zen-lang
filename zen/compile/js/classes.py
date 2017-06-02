import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.functions import *
from zen.compile.js.util import *


# Compile a (class ...) expression
def compileClass(node, env):
    name, args = node.values[1], node.values[2:]
    assert name.cls is ast.Symbol
    symbol = env.create(name.value)
    inits, methods = compileClassComponents(args, env)

    cls = js.Class(env=env, name=name.value, inits=inits, methods=methods)
    symbol.contents = cls

    return [js.Operator(
        op = '=',
        left = symbol,
        right = cls)]


# Compile an (extend ...) expression
def compileExtend(node, env):
    name, args = node.values[1], node.values[2:]
    assert name.cls is ast.Symbol
    symbol = env.find(name.value)
    cls = symbol.contents
    assert cls.cls is js.Class

    inits, methods = compileClassComponents(args, env)
    cls.inits += inits
    cls.methods += methods

    return []


# Helper method to compile all of the different components in a class definition
def compileClassComponents(args, env):
    inits = []
    methods = []
    keywords = getKeywords(args)

    for arg in args[len(keywords) * 2:]:
        if (arg.cls is ast.List and
            len(arg.values) > 2 and
            arg.values[0].cls is ast.Symbol):

            if (arg.values[0].value == 'def' and
                arg.values[1].cls is ast.List):
                method = compileMethod(
                    ast.List(None, values=(
                        [ast.Symbol(None, value='def-method')] +
                        arg.values[1:])), env)

                methods.append(method)

            elif arg.values[0].value == 'init':
                init = compileInit(arg, env)
                inits.append(init)

    return inits, methods
