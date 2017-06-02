import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.errors import *

gensym_id = 0


# BaseEnvironment: An Environment's purpose in life is to deal with the
# relationship between Zen symbols and JavaScript symbols. The BaseEnvironment
# class contains just a few essential methods to define new symbols, look up
# existing symbols, and compile those symbols into JavaScript `var` statements.

class BaseEnvironment(object):
    def __init__(self, outer):
        self.outer = outer
        self.symbols = {}

    def __str__(self):
        return str(self.symbols)

    # .create: Create a new Zen symbol with the given name and pair it with a
    # brand new randomly-generated JavaScript symbol.

    def create(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        else:
            js_sym = self.gensym()
            self.symbols[symbol] = js_sym
            return js_sym

    # .gensym: Return a JavaScript symbol with a unique randomly-generated value.

    def gensym(self):
        global gensym_id

        symbol = '__gensym_{}'.format(gensym_id)
        gensym_id += 1
        return js.Symbol(value=symbol)

    # .find: Look up a symbol and return the corresponding JavaScript ast.Symbol
    # object. If the symbol isn't defined in this environment, we ask our
    # parent environment to find it for us.

    def find(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        else:
            return self.outer.find(symbol)

    # .compile: Return a list of all the JavaScript `var` statements for the
    # symbols in this module.

    def compile(self):
        return [js.Var(value=x.value)
                for x in self.symbols
                if x.cls is js.Symbol]

    # .outermost: Environments can be nested inside each other, and occasionally
    # these nested environments need to access symbols in the top-level module
    # environment. The .outermost method gives us easy access an environment's
    # outermost parent.

    def outermost(self):
        return self.outer.outermost()
