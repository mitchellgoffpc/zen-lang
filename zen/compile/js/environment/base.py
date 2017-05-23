"""
Provides an environment class for the compiler
"""

import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *

gensym_id = 0


# Environment base class

# Environments are all about dealing with the mapping from Zen symbols
# to JavaScript symbols
class Environment(object):
    def __init__(self, outer):
        self.outer = outer
        self.symbols = {}

    def __str__(self):
        return str(self.symbols)

    def create(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        else:
            js_sym = self.gensym()
            self.symbols[symbol] = js_sym
            return js_sym

    def gensym(self):
        global gensym_id

        symbol = '__gensym_{}'.format(gensym_id)
        gensym_id += 1
        return symbol

    def outermost(self):
        return self.outer.outermost()

    def compile(self):
        return [js.Var(value=x) for x in self.symbols]


# Function environment
class FunctionEnvironment(Environment):
    def __init__(self, outer, args={}):
        super(FunctionEnvironment, self).__init__(outer)
        assert isinstance(args, dict)
        self.args = args
        self.args['js/arguments'] = 'arguments'

    def find(self, symbol):
        if symbol in self.symbols:
            return js.Symbol(value=self.symbols[symbol])
        elif symbol in self.args:
            return js.Symbol(value=self.args[symbol])
        else:
            return self.outer.find(symbol)
