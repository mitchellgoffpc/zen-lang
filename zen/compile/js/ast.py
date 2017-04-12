"""
Provides all the classes that will make up the AST for the javascript program
"""

class Node(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs
        self.cls = self.__class__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.write()

    def write(self, indent=0):
        try:
            return self.value.write(indent)
        except AttributeError:
            return str(self.value)



# Basic node types
class Symbol(Node): pass
class Integer(Node): pass
class Float(Node): pass

class Null(Node):
    def write(self, indent=0):
        return 'null'

class String(Node):
    def write(self, indent=0):
        return '"{}"'.format(self.value)

class Array(Node):
    def write(self, indent=0):
        return '[{}]'.format(' '.join(x.write(indent) for x in self.values))

class Object(Node):
    def write(self, indent=0):
        return '{{ {} }}'.format(', '.join(
            '{}: {}'.format(k, v)
            for k, v in self.values))



# Complex node types
class Return(Node):
    def write(self, indent=0):
        return 'return {}'.format(self.value.write(indent))

class Call(Node):
    def write(self, indent=0):
        return '{}({})'.format(self.f, ', '.join(x.write(indent) for x in self.args))

class Operator(Node):
    def write(self, indent=0):
        if self.op == '.':
            fstr = '{}{}{}'
        else:
            fstr = '{} {} {}'

        return fstr.format(
            self.left.write(indent),
            self.op,
            self.right.write(indent))

class Function(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        args = ', '.join(x.write(indent) for x in self.args)
        body = (['var {}'.format(x) for x in self.env.symbols] +
                [x.write(indent + 1) for x in self.body])

        return 'function ({}) {{\n{}{}}}'.format(
            args,
            ''.join('{}    {};\n'.format(tabs, line) for line in body),
            tabs)