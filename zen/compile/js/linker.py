import os

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *
from zen.parse.parse import Parser

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity
from zen.transforms.case import resolveCase
from zen.transforms.macros import resolveMacros


class Linker(object):
    imports = [
        'library/core/core.zen',
        'library/core/types.zen']

    def __init__(self, source, main):
        self.main = main
        self.prefix = ['__int', '__str', 'print', 'call']
        self.prefix_modules = []

        if source:
            self.source = Module(self, source)
            self.modules = [self.source]
        else:
            self.source = None
            self.modules = []


    # Compile the source module
    def compile(self):
        for path in self.imports:
            path = os.path.join(self.main, path)
            module = Module(self, path)
            module.compile()

            self.prefix_modules += [module]
            self.prefix += module.env.exports()

        if self.source:
            self.source.compile()


    # Get the module at the given path, loading and compiling it if necessary
    def getModule(self, path):
        module = next((x for x in self.modules if x.source == path), None)

        if not module:
            module = Module(self, path)
            module.compile()
            self.modules += [module]

        return module


    # Link all the code we've compiled into a single javascript file
    def link(self, output):
        with open(output, 'w+') as output:
            output.write(self.write())

    def write(self):
        core = os.path.join(self.main, 'library/js/core.js')
        modules = self.prefix_modules + list(reversed(self.modules))

        with open(core, 'r') as prefix:
            return (
                prefix.read() + '\n\n' +
                '\n\n'.join(x.write() for x in modules))



class Module(object):
    def __init__(self, linker, source):
        self.linker = linker
        self.source = source
        self.env = ModuleEnvironment(self)

    def __eq__(self, other):
        return self.source == other.source


    # Read, parse, and compile a Zen source file
    def compile(self):
        with open(self.source, 'r') as code:
            source = code.read()

        # Parse the source file
        parser = Parser(source)
        nodes = parser.parse()

        # AST transforms
        transforms = [
            resolveDecorators,
            resolveFixity,
            resolveMacros,
            resolveCase]

        for transform in transforms:
            nodes = map(transform, nodes)

        nodes = filter(None, nodes)

        # Compile into Javascript code
        code = self.env.compile()
        code += [x for node in nodes for x in self.compileNode(node)]
        self.code = filter(lambda x: x.cls != js.Null, code)


    # Transform a single Zen AST node into a JavaScript AST node
    def compileNode(self, node):
        expr, code = compileExpression(node, self.env)
        return code + [expr]


    # Write out the compiled Javascript code as text
    def write(self):
        return ''.join(
            '{};\n'.format(x.write())
            for x in self.code)
