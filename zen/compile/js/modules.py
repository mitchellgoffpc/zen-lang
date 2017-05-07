import os

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *
from zen.parse.parse import Parser

from zen.library.macros.core import *

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity
from zen.transforms.case import resolveCase
from zen.transforms.macros import resolveMacros


class Module(object):
    def __init__(self, linker, source):
        assert source != '__int'

        self.linker = linker
        self.source = source
        self.env = ModuleEnvironment(self)

    def exports(self):
        return self.env.symbols

    def load(self):
        source = os.path.join(self.linker.main, self.source)

        with open(source, 'r') as code:
            return code.read()


    # Populate this module with the exports of module y
    def populate(self, module):
        for target in module.exports():
            self.env.imports[target] = (module, target)


    # Read, parse, and compile a Zen source file
    def compile(self):
        source = self.load()
        parser = Parser(source)
        nodes = parser.parse()

        # AST transforms
        transforms = [
            resolveDecorators,
            resolveFixity,
            resolveMacros]

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



# A dummy module that allows us to access built-in js functionality
class JSModule(Module):
    def __init__(self, linker, source, symbols=[]):
        self.linker = linker
        self.source = source
        self.symbols = symbols

    def exports(self):
        return self.symbols

    def populate(self, module):
        pass

    def compile(self):
        pass

    def write(self):
        if self.source:
            return self.load()
        else:
            return ''



# Compile an import statement
def compileImport(node, env):
    args = node.values[1:]
    imports = []
    i = 0

    while i < len(args) and not isKeyword(args[i]):
        assert args[i].cls is ast.Symbol
        imports.append(args[i].value)
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
        assert keywords['from'].cls is ast.Symbol

        if alias:
            assert len(imports) == 1

        for target in imports:
            env.outermost().createImport(
                target = target,
                ns = keywords['from'].value,
                alias = alias)

    # import
    else:
        assert len(imports) == 1

        env.outermost().createImport(
            target = imports[0],
            ns = imports[0],
            alias = alias)

    return js.Null(), []
