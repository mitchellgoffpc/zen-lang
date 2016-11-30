"""
Provides an environment class for the compiler
"""

from zen.compile.errors import *

sym_id = 0


# Environment base class
class Environment(object):
    def __init__(self):
        self.symbols = {}

    def __str__(self):
        return str(self.symbols)

    def create(self, symbol, type):
        if self.symbols.get(symbol, type) != type:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            self.symbols[symbol] = type

    def gen(self):
        global sym_id
        sym_id += 1
        return 'gensym_{}'.format(sym_id)



# Global environment
class GlobalEnvironment(Environment):
    def __init__(self):
        super(GlobalEnvironment, self).__init__()
        self.assignments = {}
        self.imports = {}

    def assign(self, symbol, type, value):
        self.create(symbol, type)
        self.assignments[symbol] = value

    def include(self, symbol, type):
        if self.imports.get(symbol, type) != type:
            raise CompileError('Symbol `{}` is already defined in an imported file'.format(symbol))
        else:
            self.imports[symbol] = type

    def find(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif symbol in self.imports:
            return self.imports[symbol]
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self

    def write(self):
        return [ self._write(symbol, type)
                 for symbol, type
                 in self.symbols.items() ]

    def _write(self, symbol, type):
        from zen.compile.write import (
            writeType,
            writeFunction,
            writeExpression)

        if symbol not in self.assignments:
            return '{} {};'.format(type, symbol)
        elif type[0] == 'FUNC':
            return writeFunction(self.assignments[symbol])
        else:
            return '{} {} = {};'.format(
                writeType(type),
                symbol,
                writeExpression(self.assignments[symbol]))



# Function environment
class FunctionEnvironment(Environment):
    def __init__(self, outer, args={}):
        super(FunctionEnvironment, self).__init__()
        self.outer = outer
        self.args = args

    def create(self, symbol, type):
        if self.args.get(symbol, type) != type:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            return super(FunctionEnvironment, self).create(symbol, type)

    def create_arg(self, symbol, type):
        if self.args.get(symbol, type) != type:
            raise CompileError('Argument `{}` is already defined'.format(symbol))
        else:
            self.args[symbol] = type

    def find(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif symbol in self.args:
            return self.args[symbol]
        else:
            return self.outer.find(symbol)

    def outermost(self):
        return self.outer.outermost()

    def write(self):
        from zen.compile.write import writeType

        return [ '{} {};'.format(writeType(type), symbol)
                 for symbol, type
                 in self.symbols.items() ]
