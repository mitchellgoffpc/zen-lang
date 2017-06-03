import os
import subprocess
import tempfile

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.linker import *
from zen.compile.js.literals import *
from zen.compile.js.util import *
from zen.parse.parse import Parser

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity


# Compile a def-macro statement into a js.Macro
def compileMacro(node, env):
    assert len(node.values) == 4
    assert node.values[1].cls in (ast.Symbol, ast.Operator)
    assert node.values[2].cls is ast.List

    name = node.values[1].value
    args = node.values[2]
    macro_env = FunctionEnvironment(env, [x.value for x in args.values])
    code = compileExpression(node.values[3], macro_env)
    retexpr = code.pop()
    body = code + [js.Return(value=retexpr)]

    js_args = [macro_env.find(x.value) for x in args.values]
    env.outermost().createMacro(name, args, js.Function(env=macro_env, args=js_args, body=body))

    return []


# Execute a macro, parse the output, and compile it into JavaScript.
def executeMacro(node, env, macro):
    args, f = macro
    quoted = [quote(x, env)[0] for x in node.values[1:]]

    macro_code = [
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
    linker = env.outermost().module.linker

    code = linker.write()
    code += ''.join('{};\n'.format(x.write()) for x in macro_code)

    # Dump the macro code to a place where we can easily find it for
    # debugging purposes
    with open('/Users/mitchell/Desktop/macro.js', 'w+') as dump:
        dump.write(code)

    # Write the macro code to a temporary file, then run the macro by calling
    # Node.js as a subprocess and having it print the macro's result to stdout.
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
        resolveFixity]

    for transform in transforms:
        node = transform(node)

    return compileExpression(node, env)
