import os
import collections

from zen.compile.js.modules import *


class Linker(object):
    def __init__(self, source, main):
        self.main = main
        self.prefix = {}
        self.macros = {}

        self.modules = collections.OrderedDict([
            ('js/util', JSModule(self, None, symbols={
                'Set': 'Set',
                'Map': 'Map'})),
            ('js', JSModule(self, os.path.join(self.main, 'library/js/core.js'), symbols={
                'true': 'true',
                'false': 'false',
                'null': 'null',

                'log': 'log',
                'call': 'call',

                'new': '__new',
                'bool': '__bool',
                'int': '__int',
                'str': '__str',

                'is-type?': 'is_type',
                'int-to-string': 'int_to_string',
                'string-to-int': 'string_to_int'}))])

        self.stdlib = collections.OrderedDict([
            ('zen/headers', JSModule(self, None, symbols={
                'bool': 'bool',
                'int': 'int',
                'str': 'str'})),
            ('zen/macros', Module(self, os.path.join(self.main, 'library/macros/core.zen'))),
            ('zen/operators', Module(self, os.path.join(self.main, 'library/core/operators.zen'))),
            ('zen/core', Module(self, os.path.join(self.main, 'library/core/core.zen'))),
            ('zen/types', Module(self, os.path.join(self.main, 'library/core/types.zen')))])

        if source:
            self.source = Module(self, source)
        else:
            self.source = None


    # Compile the source module
    def compile(self):
        for ns, module in self.stdlib.items():
            module.ns = ns
            module.compile()
            self.modules[ns] = module
            self.prefix.update(module.exports())
            self.macros.update(module.macros())

        if self.source:
            self.source.compile()
            self.modules['main'] = self.source
        else:
            path = os.path.join(self.main, 'bin/stdlib.js')
            self.link(path)


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
