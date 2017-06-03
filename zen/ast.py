# This module contains the building blocks for a Zen AST

class Location(object):
    def __init__(self, start, end, source=None):
        self.start, self.end, self.source = start, end, source

# Node is the base class for all the different types of Zen AST nodes.
class Node(object):
    def __init__(self, parser, **kwargs):
        if parser:
            start = kwargs.pop('start', parser.token.start)

            if kwargs.pop('advance', False):
                parser.advance()

            kwargs['loc'] = Location(start, parser.prev_end, parser.source)

        self.__dict__ = kwargs
        self.cls = self.__class__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.value)


class Symbol(Node): pass
class Operator(Node): pass

class Nil(Node):
    def __str__(self):
        return 'nil'

class Boolean(Node):
    def __str__(self):
        return 'true' if self.value else 'false'

class Integer(Node): pass
class Float(Node): pass

class String(Node):
    def __str__(self):
        return '"{}"'.format(self.value)

class List(Node):
    fstr = '({})'

    def __str__(self):
        return self.fstr.format(' '.join(str(x) for x in self.values))

class Array(List):
    fstr = '[{}]'

class Map(List):
    fstr = '{{{}}}'
