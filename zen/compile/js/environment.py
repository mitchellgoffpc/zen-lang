"""
Provides an environment class for the compiler
"""

import zen.compile.js.ast as js
from zen.compile.js.errors import *

sym_id = 0


# Environment base class
class Environment(object):
    def __init__(self):
        self.symbols = []

    def __str__(self):
        return str(self.symbols)

    def create(self, symbol):
        if symbol in self.symbols:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            self.symbols.append(symbol)

    def gen(self):
        global sym_id
        sym_id += 1
        return 'gensym_{}'.format(sym_id)



# Global environment
class GlobalEnvironment(Environment):
    def __init__(self):
        super(GlobalEnvironment, self).__init__()
        self.symbols += ['print']
        self.assignments = {}
        self.imports = {}

    def assign(self, symbol, value):
        self.create(symbol, type)
        self.assignments[symbol] = value

    def include(self, symbol):
        if self.imports.get(symbol, type) != type:
            raise CompileError('Symbol `{}` is already defined in an imported file'.format(symbol))
        else:
            self.imports[symbol] = type

    def find(self, symbol):
        if symbol in self.symbols:
            return js.Symbol(value=symbol)
        elif symbol in self.imports:
            return self.imports[symbol]
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self



# Function environment
class FunctionEnvironment(Environment):
    def __init__(self, outer, args=[]):
        super(FunctionEnvironment, self).__init__()
        self.outer = outer
        self.args = args

    def create(self, symbol):
        if symbol in self.args:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            return super(FunctionEnvironment, self).create(symbol)

    def create_arg(self, symbol):
        if symbol in self.args:
            raise CompileError('Argument `{}` is already defined'.format(symbol))
        else:
            self.args.append(symbol)

    def find(self, symbol):
        if symbol in self.symbols or symbol in self.args:
            return js.Symbol(value=symbol)
        else:
            return self.outer.find(symbol)

    def outermost(self):
        return self.outer.outermost()
