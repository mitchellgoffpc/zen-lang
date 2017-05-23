import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.functions import *
from zen.library.macros.core import *



# Class compiler
def compileClass(node, env):
    name, args = node.values[1].value, node.values[2:]
    keywords = getKeywords(args)
    symbol = env.create(name)

    cls_env = ClassEnvironment(env)
    dummy_env = FunctionEnvironment(env)
    new_env = MethodEnvironment(dummy_env)

    methods = []
    properties = []
    initializers = []

    for arg in args[len(keywords) * 2:]:
        if (arg.cls is ast.List and
            len(arg.values) > 2 and
            arg.values[0].cls is ast.Symbol):

            if (arg.values[0].value == 'def' and
                arg.values[1].cls is ast.List):
                method = compileMethod(
                    ast.List(None, values=(
                        [Symbol(None, value='def-method')] +
                        arg.values[1:])), env)

                if method:
                    methods.append(method)

            elif arg.values[0].value == 'var':
                properties.append(arg)

            elif arg.values[0].value == 'init':
                compileInit(arg, cls_env)

    f = js.Function(env=dummy_env, args=[], body=[
        js.Var(value='cls'),
        js.Var(value='__new'),

        js.Operator(
            op = '=',
            left = js.Symbol(value='cls'),
            right = JSObject('class',
                __name = js.String(value=symbol),
                __init = cls_env.init,
                __methods = js.Object(values=methods))),

        js.Operator(
            op = '=',
            left = js.Symbol(value='__new'),
            right = js.Function(env=new_env, args=[], body=[js.Return(
                value = JSObject('object',
                    __class = js.Symbol(value='cls'),
                    __properties = js.Object(values=[])))])),

        js.Operator(
            op = '=',
            left = js.Operator(
                op = '.',
                left = js.Symbol(value='cls'),
                right = js.Symbol(value='__new')),
            right = js.Symbol(value='__new')),

        js.Return(value=js.Symbol(value='cls'))])

    return js.Operator(
        op = '=',
        left = js.Symbol(value=symbol),
        right = js.Call(f=f, args=[])), []



def compileInitCall(node, env):
    assert env.__class__ is InitEnvironment

    a = [compileExpression(x, env)
         for x in node.values[1:]]

    args = [x for x, _ in a]
    code = [x for _, c in a for x in c]

    return js.Call(
        f = js.Operator(
            op = '.',
            left = js.Operator(
                op = '.',
                left = js.Symbol(value='_self'),
                right = js.Symbol(value='__class')),
            right = js.Symbol(value='__init')),
        args = [js.Symbol(value='_self')] + args), code
