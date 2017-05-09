"""
Provides an environment class for the compiler
"""

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *

gensym_id = 0


# Environment base class
class Environment(object):
    def __init__(self):
        self.symbols = {}

    def __str__(self):
        return str(self.symbols)

    def create(self, symbol, js_symbol=None):
        if symbol in self.symbols:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            self.symbols[symbol] = (js_symbol or symbol)

    def gensym(self):
        global gensym_id

        symbol = '__gensym_{}'.format(gensym_id)
        gensym_id += 1
        return symbol

    def outermost(self):
        return self.outer.outermost()


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

    def compile(self):
        return [js.Var(value=x) for x in self.symbols]
