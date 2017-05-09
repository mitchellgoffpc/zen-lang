import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.compile.js.environment.base import *
from zen.compile.js.environment.classes import *


# Root environment
class ModuleEnvironment(Environment):
    def __init__(self, module):
        super(ModuleEnvironment, self).__init__()
        self.module = module
        self.imports = {}
        self.macros = {}

    def createImport(self, target, ns, alias=None):
        module = self.module.linker.getModule(ns)

        if target:
            if target in module.exports():
                self.imports[alias or target] = (module, target)
            elif target in module.macros():
                self.macros[alias or target] = module.macros[target]
            else:
                raise CompileError('Module `{}` has no symbol `{}`'.format(ns, target))

        else:
            for target in module.exports():
                symbol = '{}/{}'.format(alias or ns, target)
                self.imports[symbol] = (module, target)
            for target, macro in module.macros().items():
                symbol = '{}/{}'.format(alias or ns, target)
                self.macros[symbol] = macro

    def createMacro(self, name, args, body):
        self.macros[name] = (args, body)

    def find(self, symbol):
        if symbol in self.symbols:
            return js.Symbol(value=self.symbols[symbol])
        elif symbol in self.imports:
            return js.Symbol(value=symbol)
        elif symbol in self.module.linker.prefix:
            return js.Symbol(value=self.module.linker.prefix[symbol])

        elif symbol in self.macros:
            return js.Macro(value=symbol, macro=self.macros[symbol])
        elif symbol in self.module.linker.macros:
            return js.Macro(value=symbol, macro=self.module.linker.macros[symbol])
        else:
            raise CompileError('Symbol `{}` is undefined in the current environment'.format(symbol))

    def outermost(self):
        return self

    def compile(self):
        return [js.Var(value=x) for x in self.symbols]
