import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.compile.js.environment.base import *
from zen.compile.js.environment.classes import *


# Root environment
class ModuleEnvironment(Environment):
    gensym_id = 0

    def __init__(self, module):
        super(ModuleEnvironment, self).__init__()
        self.module = module
        self.imports = {}
        self.macros = {}

    def createImport(self, target, ns, alias=None):
        module = self.module.linker.getModule(ns)
        self.imports[alias or target] = (module, target)

        if target not in module.exports():
            raise CompileError('Module `{}` has no symbol `{}`'.format(ns, target))

    def createMacro(self, name, args, body):
        self.macros[name] = (args, body)

    def find(self, symbol):
        if (symbol in self.symbols or
            symbol in self.imports or
            symbol in self.module.linker.prefix):
            return js.Symbol(value=symbol)
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self

    def compile(self):
        return [js.Var(value=x) for x in self.symbols]
