"""
Provides all the classes that will make up the AST for the javascript program
"""

from zen.transforms.case import recase


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
class Integer(Node): pass
class Float(Node): pass

class Symbol(Node):
    def write(self, indent=0):
        return recase(self.value)

class Boolean(Node):
    def write(self, indent=0):
        return 'true' if self.value else 'false'

class Null(Node):
    def write(self, indent=0):
        return 'null'

class String(Node):
    def write(self, indent=0):
        return '"{}"'.format(self.value)

class Array(Node):
    def write(self, indent=0):
        return '[{}]'.format(', '.join(x.write(indent) for x in self.values))

class Object(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * (indent + 1)
        return '{{{}}}'.format(', '.join(
            '\n{}{}: {}'.format(tabs, k.write(indent + 1), v.write(indent + 1))
            for k, v in self.values
            if v))



# Complex node types
class Var(Node):
    def write(self, indent=0):
        return 'var {}'.format(self.value)

class Return(Node):
    def write(self, indent=0):
        return 'return {}'.format(self.value.write(indent))

class Index(Node):
    def write(self, indent=0):
        return '{}[{}]'.format(
            self.list.write(indent),
            self.index.write(indent))

class Call(Node):
    def write(self, indent=0):
        args = ', '.join(x.write(indent) for x in self.args)
        fstr = '{}({})' if self.f.cls is Symbol else '({})({})'

        return fstr.format(self.f.write(indent), args)


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
        body = [x.write(indent + 1) for x in self.env.compile() + self.body]

        return 'function ({}) {{\n{}{}}}'.format(
            ', '.join(x.write(indent) for x in self.args),
            ''.join('{}    {};\n'.format(tabs, line) for line in body),
            tabs)


class IfElse(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        cond = self.cond.write(indent)
        x = [a.write(indent + 1) for a in self.x]
        y = [a.write(indent + 1) for a in self.y]

        return 'if ({}) {{\n{}{}}} else {{\n{}{}}}'.format(
            cond,
            ''.join('{}    {};\n'.format(tabs, line) for line in x),
            tabs,
            ''.join('{}    {};\n'.format(tabs, line) for line in y),
            tabs)


class While(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        cond = self.cond.write(indent)
        body = [x.write(indent + 1) for x in self.body]

        return 'while ({}) {{\n{}{}}}'.format(
            cond, ''.join('{}    {};\n'.format(tabs, line) for line in body))



# Alternative node types

# These classes are for AST nodes that aren't real javascript AST nodes, but
# are still useful for various reasons.

class Macro(Node):
    pass

class Conditional(Node):
    pass

class ErrorConditional(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        fstr = ' else {{\n{}    throw Error("Condition fell through");\n{}}}'
        return fstr.format(tabs, tabs);


class ConditionalFunction(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        args = ', '.join(x.write(indent) for x in self.args)
        conditions = MultiIfElse(conditionals=self.conditionals)
        error = ErrorConditional()

        return 'function ({}) {{\n{}    {}{}}}'.format(
            args,
            tabs,
            conditions.write(indent + 1),
            error.write(indent + 1))


class MultiIfElse(Node):
    def write(self, indent=0):
        tabs = ' ' * 4 * indent
        result = ''

        for i, cond in enumerate(self.conditionals):
            if i == len(self.conditionals) - 1:
                fstr = 'if ({}) {{\n{}{}}}'
            else:
                fstr = 'if ({}) {{\n{}{}}} else '

            result += fstr.format(
                cond.test,
                ''.join('{}    {};\n'.format(tabs, x.write(indent + 1)) for x in cond.body),
                tabs)

        return result
