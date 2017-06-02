import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.environment.base import *
from zen.compile.js.environment.functions import *


# MethodEnvironment
# TODO: Document
class MethodEnvironment(FunctionEnvironment):
    def find(self, symbol):
        if symbol == 'self':
            return js.Symbol(value='_self')
        else:
            return super(MethodEnvironment, self).find(symbol)


# Init environment
# TODO: Document
class InitEnvironment(MethodEnvironment):
    pass
