"""
Provides error classes which can be thrown by the compiler
"""

from zen.errors import ZenError


# Base class for all compiler errors 
class CompileError(ZenError):
    def __str__(self):
        return 'CompileError: {}'.format(self.detail)


# Error for function call with the wrong number of arguments
class ArgumentError(CompileError):
    def __init__(self, function, actual, min, max):
        self.function, self.actual, self.min, self.max = function, actual, min, max

    def __str__(self):
        if self.actual < self.min:
            return ('ArgumentError: ({} ...) requires at least {} arguments ' +
                    '({} given)'.format(self.function, self.min, self.actual))
        else:
            return ('ArgumentError: ({} ...) takes at most {} arguments ' +
                    '({} given)'.format(self.function, self.max, self.actual))
