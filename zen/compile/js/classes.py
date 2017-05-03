import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.library.macros.core import *



# Class compiler
def compileClass(node, env):
    name = node.values[1].value
    keywords = getKeywords(node.values[2:])
    env.create(name)

    cls_env = ClassEnvironment(env)
    dummy_env = FunctionEnvironment(env)
    new_env = MethodEnvironment(dummy_env)

    methods = [compileMethod(x, cls_env) for x in keywords['methods'].values]

    f = js.Function(env=dummy_env, args=[], body=[
        js.Var(value='cls'),
        js.Var(value='factory'),

        js.Operator(
            op = '=',
            left = js.Symbol(value='cls'),
            right = JSObject('class',
                __default_methods = js.Object(values=methods))),

        js.Operator(
            op = '=',
            left = js.Symbol(value='factory'),
            right = js.Function(env=new_env, args=[], body=[js.Return(
                value = JSObject('object',
                    __value = js.Object(values=[]),
                    __class = js.Symbol(value='cls'),
                    __methods = js.Object(values=[])))])),

        js.Operator(
            op = '=',
            left = js.Operator(
                op = '.',
                left = js.Symbol(value='cls'),
                right = js.Symbol(value='__new')),
            right = js.Symbol(value='factory')),

        js.Return(value=js.Symbol(value='cls'))])

    return js.Operator(
        op = '=',
        left = js.Symbol(value=name),
        right = js.Call(f=f, args=[])), []



# Method compiler
def compileMethod(node, env):
    assert node.cls is List
    assert len(node.values) >= 3
    assert node.values[1].cls is List
    assert len(node.values[1].values) > 0

    args, body = node.values[1], node.values[2:]
    method_env = MethodEnvironment(env, args=args.values)
    do_expr = List(None, values=[Symbol(None, value='do')] + body)

    selector = ''.join(
        ':{}'.format(arg.values[1].value)
        for arg in args.values
        if isKeyword(arg))

    args = ([js.Symbol(value='self')] +
            [js.Symbol(value=arg.value)
                for arg in args.values
                if arg.cls is Symbol])

    retexpr, code = compileExpression(do_expr, method_env)
    body = code + [js.Return(value=retexpr)]
    method = js.Function(env=method_env, args=args, body=body)

    return (js.String(value=selector), method)
