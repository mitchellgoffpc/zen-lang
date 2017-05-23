import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *


# An Unpacker is an object to help us "unpack" a single argument in a list
# into whatever variable(s) we desire. An unpacker may also place certain
# restrictions on the value or type of the argument.

class Unpacker(object):
    def __init__(self, i, arg):
        self.i = js.Integer(value=i)
        self.arg = js.Symbol(value=arg.value)

    def symbol(self, env):
        return (self.arg.value, self.arg.value)

    def compileUnpack(self, env, source):
        return [js.Operator(
            op = '=',
            left = self.arg,
            right = js.Index(list=env.find(source), index=self.i))]



# A DefaultUnpacker is a catch-all condition for when no restrictions on the
# argument are given.

class DefaultUnpacker(Unpacker):
    def compileCondition(self, env, source):
        return js.Boolean(value=True)



# A LiteralUnpacker accepts an argument with a specific VALUE, usually an int or
# string literal.

class LiteralUnpacker(Unpacker):
    def __init__(self, i, value):
        self.i = js.Integer(value=i)
        self.value = value

    def symbol(self):
        return None

    def compileCondition(self, env, source):
        return js.Operator(
            op = '==',
            left = js.Index(list=env.find(source), index=self.i),
            right = self.value)

    def compileUnpack(self, env, source):
        return [js.Null()]



# A TypeUnpacker accepts an argument with a specific CLASS.

class TypeUnpacker(Unpacker):
    def __init__(self, i, arg, type):
        super(TypeUnpacker, self).__init__(i, arg)
        self.type = js.Symbol(value=type.value)

    def compileCondition(self, env, source):
        f = env.find('js/is-type?')

        return js.Operator(
            op = '.',
            left = js.Call(
                f = js.Symbol(value='__dispatch'),
                args = [
                    f,
                    js.Index(list=env.find(source), index=self.i),
                    self.type]),
            right = js.Symbol(value='__value'))

    def compileUnpack(self, env, source):
        return [js.Operator(
            op = '=',
            left = self.arg,
            right = js.Index(list=env.find(source), index=self.i))]



# A RemainingUnpacker packs all the remaining arguments into a single array.
class RemainingUnpacker(Unpacker):
    def compileUnpack(self, env, source):
        return [js.Operator(
            op = '=',
            left = self.arg,
            right = js.Call(
                f = js.Operator(
                    op = '.',
                    left = js.Symbol(value='arguments'),
                    right = js.Symbol(value="slice")),
                args = [self.i]))]
