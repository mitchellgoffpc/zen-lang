import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.errors import *
from zen.library.macros.core import *


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



def compileImport(node, env):
    args = node.values[1:]
    imports = []
    i = 0

    while i < len(args) and not isKeyword(args[i]):
        imports.append(args[i])
        i += 1

    keywords = getKeywords(args[i:])


    # import :as
    if 'as' in keywords:
        assert len(imports) == 1
        assert keywords['as'].cls is ast.Symbol

        alias = keywords['as'].value
    else:
        alias = None

    # import :from
    if 'from' in keywords:
        path = []
        node = keywords['from']

        if node.cls is ast.String:
            path = node.value
        else:
            path = unwind(node)

        for item in imports:
            assert item.cls is ast.Symbol
            env.outermost().createImport(target=item.value, path=path)

    # import
    else:
        assert len(imports) == 1

        path = unwind(imports[0])
        env.outermost().createImport(target=path[-1], path=path[:-1])

    return js.Null(), []



# Class compilers
def compileClass(node, env):
    name = node.values[1]
    keywords = getKeywords(node.values[2:])
    cls_env = ClassEnvironment(outer=env)
    outer = env.outermost()

    methods = [compileMethod(x, cls_env) for x in keywords['methods'].values]
    outer.createClass(env, name, methods)

    return js.Null(), []

def compileMethod(node, env):
    return js.Null()



# Literal compilers
def compileKeyword(node, env):
    assert isKeyword(node)
    return js.Object(values=[
        (js.String(value='__type'), js.String(value='keyword')),
        (js.String(value='__value'), js.String(value=node.values[1].value))]), []


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

    return js.Object(values=[
        (js.String(value='__type'), js.String(value='map')),
        (js.String(value='__value'), js.Object(values=cells))]), code


def compileLambda(node, env):
    if len(node.values) != 3:
        raise ArgumentError('lambda', len(node.values) - 1, 2, 2)

    _, args, body = node.values

    func_env = FunctionEnvironment(env, [arg.value for arg in args.values])
    retexpr, code = compileExpression(body, func_env)
    body = code + [js.Return(value=retexpr)]
    args = [js.Symbol(value=arg) for arg in args.values]

    return js.Object(values=[
        (js.String(value='__type'), js.String(value='string')),
        (js.String(value='__value'), js.Function(env=func_env, args=args, body=body))]), []



# Primitive dispatch
primitives = {
    'do': compileDo,
    'var': compileVar,
    'map': compileMap,
    'keyword': compileKeyword,
    'lambda': compileLambda,
    'def_class': compileClass,
    'def_method': compileMethod,
    'import': compileImport }
