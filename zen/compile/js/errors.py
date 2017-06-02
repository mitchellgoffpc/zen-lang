from zen.errors import ZenError


# CompileError: The base class for all compiler errors.

class CompileError(ZenError):
    name = 'Compile-Error'

    def __init__(self, message):
        super(ZenError, self).__init__(message)
        self.module = None

    def __str__(self):
        if self.module:
            return '({}\n    :in {}\n    :error "{}")'.format(
                self.name,
                self.module.ns,
                self.message)

        else:
            return '({}\n    :error "{}")'.format(
                self.name,
                self.message)



# ArgumentError: Gets thrown when a primitive function is called with the wrong
# number of arguments.

class ArgumentError(CompileError):
    name = 'Argument-Error'

    def __init__(self, f, actual, min, max):
        super(ArgumentError, self).__init__(None)
        self.f, self.actual, self.min, self.max = f, actual, min, max

        if self.actual < self.min:
            self.message = '({} ...) takes at least {} arguments ({} given)'.format(
                self.f,
                self.min,
                self.actual)
        else:
            self.message = '({} ...) takes at most {} arguments ({} given)'.format(
                self.f,
                self.max,
                self.actual)



# ReferenceError: Gets thrown when a ModuleEnvironment can't find a symbol.

class ReferenceError(CompileError):
    name = 'Reference-Error'

    def __init__(self, symbol):
        self.message = '(symbol {}) hasn\'t been defined yet!'.format(symbol)
