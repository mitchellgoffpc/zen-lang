import os
import re

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.parse.parse import Parser

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity


# A BaseModule object represents a single Zen module, and contains most of the
# methods we need to compile Zen code into JavaScript. We initialize a
# BaseModule with a string containing Zen code, and the .compile method
# transforms this string into a list of JavaScript AST nodes. By a happy
# coindence, these new AST nodes know how to render themselves into strings,
# so the .write method just joins them all together and returns the module's
# entire JavaScript code.

class BaseModule(object):
    def __init__(self, linker, source):
        self.linker = linker
        self.source = source
        self.env = ModuleEnvironment(self)
        self.ns = None


    # Return a dict of all the symbols and macros that are defined in
    # this module
    def exports(self):
        return self.env.symbols


    # Read, parse, and compile a Zen source file
    def compile(self):
        # First we parse the Zen source code into a list of Zen AST nodes
        parser = Parser(self.source)
        nodes = parser.parse()

        # Then we do some AST transforms
        transforms = [
            resolveDecorators,
            resolveFixity]

        for transform in transforms:
            nodes = map(transform, nodes)

        nodes = filter(None, nodes)

        # Then we compile our Zen ASTs into a list of Javascript ASTs
        code = self.env.compile()
        code += [x for node in nodes
                   for x in self.compileNode(node)]

        # Then we filter out the nulls, and we're done!
        self.code = filter(lambda x: x.cls != js.Null, code)


    # Transform a single Zen AST node into a list of JavaScript AST nodes
    def compileNode(self, node):
        try:
            return compileExpression(node, self.env)
        except CompileError as e:
            if not hasattr(e, 'module'):
                e.module = self
            raise


    # Render all of the JavaScript AST nodes in this module into a single string
    def write(self):
        return ''.join(
            '{};\n'.format(x.write())
            for x in self.code)



# A BaseJSModule is a module that contains JavaScript code instead of Zen
# code. This allows us to link raw JavaScript code into a project as necessary.

# Sometimes, when linking raw JavaScript into our Zen code, we need to
# reference objects which are defined in Zen modules. The Zen compiler does
# not (yet) let us import any Zen module we want into our JavaScript code, but
# it does let us reference any symbol in the Zen Prelude, which does the trick
# for now. See .write() for details.

# TODO: Make it possible to import symbols from other modules

class BaseJSModule(BaseModule):
    def __init__(self, linker, source, symbols={}):
        super(BaseJSModule, self).__init__(linker, source)
        self.symbols = {x: js.Symbol(value=y) for x, y in symbols.items()}

    def exports(self):
        return self.symbols

    def macros(self):
        return {}

    def populate(self, module):
        pass

    def compile(self):
        pass

    # The Zen Prelude begins with some raw JavaScript, and this JavaScript code
    # needs access to some symbols which aren't defined until later on in the
    # Prelude (in particular, Bool, Int & String). For the sake of simplicity,
    # we just wait until the rendering phase to link these symbols into the
    # code. Then we scan the source file and replace all instances of
    # `#{<symbol>}` with the corresponding symbol from the Prelude.

    def write(self):
        source = self.source

        for match in re.finditer(r"#\{(.*?)\}", source):
            symbol = match.group(1)
            js_symbol = self.linker.prelude_symbols.get(symbol)

            if js_symbol and js_symbol.cls is js.Symbol:
                source = re.sub(
                    "#{{{}}}".format(symbol),
                    js_symbol.write(),
                    source)
            else:
                raise CompileError("Zen symbol `{}` is undefined".format(symbol))

        return source



# The FileModule mixin is a subclass of BaseModule that uses a file
# as its source instead of a string.

class FileModule(object):
    def __init__(self, linker, source, **kwargs):
        source = self.load(source) if source else ''
        super(FileModule, self).__init__(linker, source, **kwargs)

    def load(self, source):
        with open(source, 'r') as code:
            return code.read()


# The Module and JSModule classes are just subclasses of BaseModule with the
# FileModule mixin.

class Module(FileModule, BaseModule): pass
class JSModule(FileModule, BaseJSModule): pass
