import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.environment.base import *


# FunctionEnvironment: A FunctionEnvironment is a subclass of BaseEnvironment
# which manages all of the symbols inside a JavaScript function. We initialize
# a FunctionEnvironment with a list of the function's arguments, and the .find
# method makes those arguments' symbols available within the function body.

class FunctionEnvironment(BaseEnvironment):
    def __init__(self, outer, args=[]):
        super(FunctionEnvironment, self).__init__(outer)
        self.args = {'js/arguments': js.Symbol(value='arguments')}
        self.args.update({arg: self.gensym() for arg in args})

    def find(self, symbol):
        if symbol in self.args:
            return self.args[symbol]
        else:
            return super(FunctionEnvironment, self).find(symbol)
