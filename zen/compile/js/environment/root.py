import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.compile.js.environment.base import *
from zen.compile.js.environment.classes import *


# Root environment
class RootEnvironment(Environment):
    def __init__(self):
        super(RootEnvironment, self).__init__()
        self.symbols += ['print']
        self.imports = {}
        self.assignments = {}
        self.classes = {}

    def assign(self, symbol, value):
        self.create(symbol, type)
        self.assignments[symbol] = value

    def createImport(self, target, path, alias=None):
        self.imports[alias or target] = (path, target)

    def createClass(self, env, name, methods):
        self.classes[name] = (env, methods)

    def find(self, symbol):
        if (symbol in self.symbols or
            symbol in self.imports or
            symbol in self.classes):
            return js.Symbol(value=symbol)
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self



    # Compile
    def compile(self):
        return [self.compileImport(name, path, target)
                for name, (path, target) in self.imports.items()]


    # Compile imports
    def compileImport(self, name, path, target):
        path = '.'.join(path + [target])

        return js.Operator(
            op = '=',
            left = js.Symbol(value=name),
            right = js.Call(
                f = js.Symbol(value='require'),
                args = [js.String(value=path)]))
