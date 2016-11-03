"""
Defines the classes which make up the AST for the target language
"""


# Type classes
class TypeConstraint:
    def __init__()


class Type:
    def __init__(self, typename):
        self.typename = typename

    def compile(self):
        return self.typename

class PrimitiveType(Type):
    pass



# Ignore for now
class PointerType(Type):
    def __init__(self, subtype):
        self.subtype = subtype

    def compile(self):
        return '{}*'.format(self.subtype.compile())

class FunctionType(object):
    def __init__(self, type, args):
        self.type, self.args = type, args

class BooleanType(Type):    name = 'int'
class CharacterType(Type):  name = 'char'
class IntegerType(Type):    name = 'int'
class FloatType(Type):      name = 'float'



# Global type list
types = [
    PrimitiveType('Int'),
    PrimitiveType('Float'),
    PrimitiveType('Char'),
    PrimitiveType('Bool') ]



# Function classes
class FunctionDeclaration:
    def __init__(self, type, name, args, body):
        self.type, self.name, self.args, self.body = type, name, args, body

    def compile(self):
        return '{} {}({}) {}'.format(
            self.type.compile(),
            self.name,
            ', '.join(arg.compile() for arg in self.args),
            self.body.compile())

class FunctionArg:
    def __init__(self, type, name):
        self.type, self.name = type, name

    def compile(self):
        return '{} {}'.format(self.type.compile(), self.name)

class FunctionReturn:
    def __init__(self, expression):
        self.expression = expression

    def compile(self):
        return 'return {};'.format(self.expression.compile())



# Statement classes
class Block:
    def __init__(self, body):
        self.body = body

    def compile(self):
        lines = [x for expr in self.body for x in expr.compile().split('\n')]
        body = '\n'.join('    {}'.format(x) for x in lines)
        return '{{\n{}\n}}'.format(body)

class IfStatement:
    def __init__(self, cond, body):
        self.cond, self.body = cond, body

    def compile(self):
        return 'if ({}) {}'.format(self.cond.compile(), self.body.compile())

class IfElseStatement:
    def __init__(self, ifs):
        self.ifs = ifs

    def compile(self):
        return ' else '.join(x.compile() for x in self.ifs)



# Expression classes
class Expression:
    pass

# FunctionCall (f: Symbol, args: [Expression])
class FunctionCall(Expression):
    def __init__(self, f, args):
        self.f, self.args = f, args

    def compile(self):
        return '{}({})'.format(self.f, ', '.join(arg.compile() for arg in self.args))

# InfixOperator (f: Symbol, args: Expression, Expression)
class InfixOperator(FunctionCall):
    def __init__(self, f, args):
        self.f, (self.left, self.right) = f, args

    def compile(self):
        return '({}) {} ({})'.format(self.left.compile(), self.f, self.right.compile())

# PrefixOperator (f: Symbol, args: Expression)
class PrefixOperator:
    def __init__(self, f, args):
        self.f, (self.right,) = f, args

    def compile(self):
        return '{}({})'.format(self.f, self.right.compile())

# Literals
class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def compile(self):
        return str(self.value)

class IntLiteral(Literal): pass
class FloatLiteral(Literal): pass
class StringLiteral(Literal): pass
