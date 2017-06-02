import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.util import *


# An Unpacker's job is to construct the run-time checks and unpacking
# code that we need to do pattern-matching for a single member in a given
# pattern. An Unpacker has two methods, .compileCondition and .compileUnpack,
# which handle the tasks of determining whether a given value matches a pattern,
# and of unpacking that value if it DOES match the pattern, respectively.

class Unpacker(object):
    def __init__(self, i, arg):
        self.i = js.Integer(value=i)
        self.arg = arg.value

    def symbol(self, env):
        return (env.find(self.arg), self.arg)

    # .compileCondition: Return a boolean condition that contains
    # any necessary checks on whether the supplied value matches the given
    # pattern.

    def compileCondition(self, env, source):
        pass

    # .compileUnpack: If the checks pass for all of a pattern's members, then
    # the pattern is a match and each Unpacker needs to unpack its value into
    # one or more JavaScript variables that correspond to the pattern's Zen
    # symbols.

    def compileUnpack(self, env, source):
        symbol = env.create(self.arg)

        return [js.Operator(
            op = '=',
            left = symbol,
            right = js.Index(list=env.find(source), index=self.i))]



# A DefaultUnpacker is a catch-all pattern-matcher for when we don't want to
# do any checks on a value at all.

class DefaultUnpacker(Unpacker):
    def compileCondition(self, env, source):
        return js.Boolean(value=True)



# A LiteralUnpacker pattern-matches an argument against a specific LITERAL
# VALUE, like an int, string or keyword.

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



# A TypeUnpacker pattern-matches a value using its CLASS.

class TypeUnpacker(Unpacker):
    def __init__(self, i, arg, type):
        super(TypeUnpacker, self).__init__(i, arg)
        self.type = type.value

    def compileCondition(self, env, source):
        f = env.find('js/is-type?')
        type = env.find(self.type)

        return js.Operator(
            op = '.',
            left = js.Call(
                f = js.Symbol(value='__dispatch'),
                args = [
                    f,
                    js.Index(list=env.find(source), index=self.i),
                    type]),
            right = js.Symbol(value='__value'))



# A RemainingUnpacker unpacks all the remaining arguments in the source list
# into a single array.

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
