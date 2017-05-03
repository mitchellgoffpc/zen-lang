import os
import subprocess
import tempfile

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.linker import *
from zen.compile.js.literals import *
from zen.library.macros.core import *
from zen.parse.parse import Parser

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity
from zen.transforms.case import resolveCase
from zen.transforms.macros import resolveMacros


# Compile a def-macro statement
def compileMacro(node, env):
    assert len(node.values) == 4
    assert node.values[1].cls is ast.Symbol
    assert node.values[2].cls is ast.List

    name = node.values[1].value
    args = node.values[2]
    macro_env = FunctionEnvironment(env, [x.value for x in args.values])
    retexpr, code = compileExpression(node.values[3], macro_env)
    body = code + [js.Return(value=retexpr)]

    js_args = [js.Symbol(value=x.value) for x in args.values]
    env.outermost().createMacro(name, args, js.Function(env=macro_env, args=js_args, body=body))

    return js.Null(), []



# Execute the given macro
def executeMacro(node, env, macro):
    args, f = env.outermost().macros[macro]
    quoted = [quote(x, env)[0] for x in node.values[1:]]

    code = [
        js.Var(value='__macro'),
        js.Operator(
            op = '=',
            left = js.Symbol(value='__macro'),
            right = f),
        js.Call(
            f = js.Symbol(value='__write'),
            args = [js.Call(
                f = js.Symbol(value='__macro'),
                args = quoted)])]

    main = os.path.join(os.path.dirname(__file__), '../../')
    core = os.path.join(main, 'library/js/core.js')

    with open(core, 'r') as prefix:
        linker = Linker(None, main)
        linker.compile()

        code = linker.write() + ''.join(
            '{};\n'.format(x.write()) for x in code)

    with open('/Users/mitchell/Desktop/macro.js', 'w+') as dump:
        dump.write(code)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(code)
        temp.flush()

        proc = subprocess.Popen(["node", temp.name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)

        zen, err = proc.communicate()

    if err:
        raise Exception(err)

    parser = Parser(zen)
    node = parser.parse()[0]

    # AST transforms
    transforms = [
        resolveDecorators,
        resolveFixity,
        resolveMacros,
        resolveCase]

    for transform in transforms:
        node = transform(node)

    return compileExpression(node, env)
