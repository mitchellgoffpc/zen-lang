import os
import collections

from zen.compile.js.modules import *


class Linker(object):
    def __init__(self, source, main):
        self.main = main
        self.prefix = []

        self.modules = collections.OrderedDict([
            ('js/util', JSModule(self, None, symbols=['Set', 'Map'])),
            ('js/core', JSModule(self, 'library/js/core.js', symbols=[
                '__int', '__str', 'print', 'call']))])

        self.stdlib = collections.OrderedDict([
            ('js/core', self.modules['js/core']),
            ('zen/core', Module(self, 'library/core/core.zen')),
            ('zen/types', Module(self, 'library/core/types.zen'))])

        if source:
            self.source = Module(self, source)
        else:
            self.source = None


    # Compile the source module
    def compile(self):
        for ns, module in self.stdlib.items():
            module.compile()
            self.modules[ns] = module
            self.prefix += module.exports()

        if self.source:
            self.source.compile()
            self.modules['main'] = self.source


    # Get the module at the given namespace, loading and compiling it if necessary
    def getModule(self, ns):
        if ns in self.modules:
            return self.modules[ns]
        else:
            module = Module(self, ns)
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
