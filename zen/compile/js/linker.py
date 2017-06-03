import os
import collections

from zen.compile.js.modules import *


# BaseLinker (Linker's parent class) is, in a sense, the top layer of the
# Zen compiler. Its job is to compile the Zen Prelude and all its imports,
# along with some raw JavaScript code, into a single js file.

class BaseLinker(object):
    def __init__(self, main):
        self.main = main
        self.prelude_symbols = {}

        # .modules is a sorted dict containining all the modules that the
        # linker has compiled so far, using the modules' namespaces as keys.

        self.modules = collections.OrderedDict([
            ('js', JSModule(self, os.path.join(self.main, 'library/js/core.js'), symbols={
                'log': 'log',
                'call': 'call',
                'index': 'index',

                'new': '__new',
                'bool': '__bool',
                'int': '__int',
                'str': '__str',

                'get-class': '__class',
                'is-type?': 'is_type',
                'int-to-string': 'int_to_string',
                'string-to-int': 'string_to_int'})),
            ('js/util', JSModule(self, None, symbols={
                'Set': 'Set',
                'Map': 'Map',
                'Array': 'Array'}))])

        # The Zen Prelude is a special set of modules that holds the core of the
        # Zen language. These modules all live in the zen/ namespace, but
        # because they contain such important functionality, the linker
        # imports their contents directly into the global namespace.

        self.prelude = collections.OrderedDict([
            ('zen/types', Module(self, os.path.join(self.main, 'library/core/types.zen'))),
            ('zen/operators', Module(self, os.path.join(self.main, 'library/core/operators.zen'))),
            ('zen/macros', Module(self, os.path.join(self.main, 'library/core/macros.zen'))),
            ('zen/methods', Module(self, os.path.join(self.main, 'library/core/methods.zen'))),
            ('zen/functions', Module(self, os.path.join(self.main, 'library/core/functions.zen')))])


    # Compile the Zen Prelude
    def compile(self):
        for ns, module in self.prelude.items():
            module.ns = ns
            module.compile()
            self.modules[ns] = module
            self.prelude_symbols.update(module.exports())


    # Get the module at the given namespace, loading and compiling it if necessary
    def getModule(self, ns):
        if ns in self.modules:
            return self.modules[ns]
        else:
            module = Module(self, os.path.join(self.main, '{}.zen'.format(ns)))
            module.ns = ns
            module.compile()
            self.modules[ns] = module
            return module


    # Link all the code we've compiled into a single javascript file
    def link(self, output):
        with open(output, 'w+') as output:
            output.write(self.write())

    def write(self):
        return '\n\n'.join(
            module.write()
            for ns, module
            in self.modules.items())



# Linker is a simple extention of BaseLinker which compiles a source module
# in addition to the Zen Prelude. The source module gets placed in the 'main'
# namespace.

class Linker(BaseLinker):
    def __init__(self, source, main):
        super(Linker, self).__init__(main)
        self.source = Module(self, source)

    def compile(self):
        super(Linker, self).compile()
        self.source.ns = 'main'
        self.source.compile()
        self.modules['main'] = self.source
