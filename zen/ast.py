"""
Provides all the classes that will make up the AST for a program
"""

class Location:
    def __init__(self, start, end, source=None):
        self.start, self.end, self.source = start, end, source

class Node:
    def __init__(self, parser, **kwargs):
        if parser:
            start = kwargs.pop('start', parser.token.start)
            
            if kwargs.pop('advance', False):
                parser.advance()

            kwargs['loc'] = Location(start, parser.prev_end, parser.source)

        self.__dict__ = kwargs
        self.cls = self.__class__
        self.type_constraints = []

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.value)


class Symbol(Node): pass
class Operator(Node): pass
class Integer(Node): pass
class Float(Node): pass
class String(Node): pass
class Boolean(Node): pass

class Cell(Node):
    def __str__(self):
        return '<{}: {}>'.format(self.key, self.value)

class List(Node):
    def __str__(self):
        return '({})'.format(' '.join(str(x) for x in self.values))