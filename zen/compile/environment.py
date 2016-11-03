"""
Provides an environment class for the compiler
"""

import zen.compile.errors


# Symbol class
class Symbol(object):
    def __init__(self, name, type, value=None):
        self.name, self.type, self.value = name, type, value


# Environment class
class Environment(object):
    def __init__(self, outer=None):
        self.symbols = dict(zip(keys, types))
        self.outer = outer

    def __str__(self):

    def find(self, key):
        if var in self:
            return self
        elif self.outer is None:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(key))
        else:
            return self.outer.find(var)

    def generate(self, type, value):
        pass
