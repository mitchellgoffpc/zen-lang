import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.environment.base import *


# Class environment
class ClassEnvironment(Environment):
    def __init__(self, outer):
        super(ClassEnvironment, self).__init__()
        self.outer = outer
        self.properties = {}
        self.methods = {}

    def find(self, symbol):
        return self.outer.find(symbol)


# Method environment
class MethodEnvironment(FunctionEnvironment):
    def find(self, symbol):
        if (symbol == 'self' or
            symbol in self.symbols or
            self.in_args(symbol)):
            return js.Symbol(value=symbol)
        else:
            return self.outer.find(symbol)

    def in_args(self, symbol):
        return any(x.value == symbol for x in self.args if x.cls is ast.Symbol)
