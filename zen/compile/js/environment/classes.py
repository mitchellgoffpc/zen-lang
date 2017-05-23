import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.environment.base import *


# Class environment
class ClassEnvironment(Environment):
    def __init__(self, outer):
        super(ClassEnvironment, self).__init__(outer)
        self.properties = {}
        self.methods = {}
        self.labels = {}
        self.init = None

    def find(self, symbol):
        if symbol in self.symbols:
            return js.Symbol(value=self.symbols[symbol])
        else:
            return self.outer.find(symbol)


# Method environment
class MethodEnvironment(FunctionEnvironment):
    def find(self, symbol):
        if symbol == 'self':
            return js.Symbol(value='_self')
        else:
            return super(MethodEnvironment, self).find(symbol)


# Init environment
class InitEnvironment(MethodEnvironment):
    pass
