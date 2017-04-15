"""
Provides an environment class for the compiler
"""

import zen.compile.js.ast as js
from zen.compile.js.errors import *

sym_id = 0


# Environment base class
class Environment(object):
    def __init__(self):
        self.symbols = []

    def __str__(self):
        return str(self.symbols)

    def create(self, symbol):
        if symbol in self.symbols:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            self.symbols.append(symbol)

    def gen(self):
        global sym_id
        sym_id += 1
        return 'gensym_{}'.format(sym_id)



# Global environment
class GlobalEnvironment(Environment):
    def __init__(self):
        super(GlobalEnvironment, self).__init__()
        self.symbols += ['print']
        self.imports = []
        self.assignments = {}
        self.classes = {}

    def assign(self, symbol, value):
        self.create(symbol, type)
        self.assignments[symbol] = value

    def createImport(self, target, path, alias=None):
        self.imports.append({'target': target, 'path': path, 'alias': alias})

    def createClass(self, env, name, methods):
        self.classes[name] = (env, methods)

    def find(self, symbol):
        if symbol in self.symbols:
            return js.Symbol(value=symbol)
        elif symbol in self.imports:
            return self.imports[symbol]
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self


    # Writers
    def write(self, indent=0):
        lines = []

        for x in self.imports:
            lines.append(self.compileImport(x))

        for cls in self.classes:
            lines.append(js.Null())

        return '\n'.join(x.write(indent=indent) for x in lines)

    def compileImport(self, obj):
        name = obj['alias'] or obj['target']
        path = '.'.join(obj['path'])

        return js.Operator(
            op = '=',
            left = js.Symbol(value=name),
            right = js.Call(
                f = js.Symbol(value='require'),
                args = [js.String(value=path)]))



# Function environment
class FunctionEnvironment(Environment):
    def __init__(self, outer, args=[]):
        super(FunctionEnvironment, self).__init__()
        self.outer = outer
        self.args = args

    def create(self, symbol):
        if symbol in self.args:
            raise CompileError('Symbol `{}` is already defined'.format(symbol))
        else:
            return super(FunctionEnvironment, self).create(symbol)

    def create_arg(self, symbol):
        if symbol in self.args:
            raise CompileError('Argument `{}` is already defined'.format(symbol))
        else:
            self.args.append(symbol)

    def find(self, symbol):
        if symbol in self.symbols or symbol in self.args:
            return js.Symbol(value=symbol)
        else:
            return self.outer.find(symbol)

    def outermost(self):
        return self.outer.outermost()



# Class environment
class ClassEnvironment(Environment):
    def __init__(self, outer):
        super(ClassEnvironment, self).__init__()
        self.outer = outer
        self.properties = {}
        self.methods = {}


# Method environment
class MethodEnvironment(FunctionEnvironment):
    def find(self, symbol):
        if symbol == 'self':
            return js.Symbol('this')
        else:
            return super(MethodEnvironment, self).find(symbol)
