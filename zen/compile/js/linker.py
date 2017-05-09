import os
import collections

from zen.compile.js.modules import *


class Linker(object):
    def __init__(self, source, main):
        self.main = main
        self.prefix = {}
        self.macros = {}

        self.modules = collections.OrderedDict([
            ('js/util', JSModule(self, None, symbols=['Set', 'Map'])),
            ('js', JSModule(self, 'library/js/core.js', symbols=[
                'log', 'call',
                'int', 'string',
                'int-to-string', 'string-to-int']))])

        self.stdlib = collections.OrderedDict([
            ('zen/core', Module(self, 'library/core/core.zen')),
            ('zen/types', Module(self, 'library/core/types.zen'))])

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
            source = os.path.join(self.main, '{}.zen'.format(ns))
            module = Module(self, source)
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
