import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *
from zen.compile.js.util import *
from zen.compile.js.environment.base import *
from zen.compile.js.environment.classes import *


# ModuleEnvironment: A ModuleEnvironment's job is to manage the symbols that are
# imported and exported from a single Zen module.

class ModuleEnvironment(BaseEnvironment):
    def __init__(self, module):
        super(ModuleEnvironment, self).__init__(None)
        self.module = module
        self.imports = {}

    # .createMacro: Register a new macro with the given name and details.

    def createMacro(self, name, args, body):
        self.symbols[name] = js.Macro(value=name, macro=(args, body))


    # .createImport: Import symbols from the module at the given namespace.

    def createImport(self, target, ns, alias=None):
        module = self.module.linker.getModule(ns)

        # If a target symbol is defined, import just that one symbol
        if target:
            if target in module.exports():
                self.imports[alias or target] = module.exports()[target]
            else:
                raise CompileError('Module `{}` has no symbol `{}`'.format(ns, target))

        # Otherwise, copy all of the module's exports into our imports
        else:
            for target, js_symbol in module.exports().items():
                symbol = '{}/{}'.format(ns, target)
                self.imports[symbol] = js_symbol


    # .find: A ModuleEnvironment is always a top-level environment, so it has
    # no .outer property. If we can't find the symbol in our imports or exports,
    # or in the Zen Prelude, we need to raise a compile error.

    def find(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        elif symbol in self.imports:
            return self.imports[symbol]
        elif symbol in self.module.linker.prelude_symbols:
            return self.module.linker.prelude_symbols[symbol]
        else:
            raise ReferenceError(symbol)


    # .outermost: We're already in the module-level environment, so just return
    # self.

    def outermost(self):
        return self
