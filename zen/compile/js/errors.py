"""
Provides error classes which can be thrown by the compiler
"""

from zen.errors import ZenError


# Base class for all compiler errors
class CompileError(ZenError):
    def __init__(self, message):
        super(ZenError, self).__init__(message)
        self.module = None

    def __str__(self):
        if self.module:
            return '(Compile-Error\n    :in {}\n    :error "{}")'.format(self.module.ns, self.message)
        else:
            return '(Compile-Error\n    :error "{}")'.format(self.message)


# Error for function call with the wrong number of arguments
class ArgumentError(CompileError):
    def __init__(self, function, actual, min, max):
        super(ArgumentError, self).__init__(None)
        self.function, self.actual, self.min, self.max = function, actual, min, max

    def __str__(self):
        if self.actual < self.min:
            return ('ArgumentError: ({} ...) requires at least {} arguments ' +
                    '({} given)').format(self.function, self.min, self.actual)
        else:
            return ('ArgumentError: ({} ...) takes at most {} arguments ' +
                    '({} given)').format(self.function, self.max, self.actual)
