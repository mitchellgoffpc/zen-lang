"""
Transforms the given source code into an abstract syntax tree
"""

from zen.ast import *
from zen.lex import Lexer
from zen.lex import TokenType
from zen.errors import SyntaxError


class Parser:
    def __init__(self, source, options={}):
        self.lexer = Lexer(source)
        self.source = source
        self.options = options
        self.prev_end = 0
        self.token = self.lexer.nextToken()


    # Parsers
    def parse(self):
        start = self.token.start
        values = self.sequence(lambda: not self.skip(TokenType.EOF), self.parseExpression)
        return values # List(self, values=values)


    def parseList(self):
        values = self.any(TokenType.PAREN_L, self.parseCellOrExpression, TokenType.PAREN_R)
        return List(self, values=values)


    def parseObject(self, isConst):
        fields = self.sequence(lambda: not self.skip(TokenType.BRACE_R), self.parseObjectField)
        return Object(self, fields=fields)


    def parseCellOrExpression(self):
        start = self.token.start
        key = self.parseExpression()

        if self.skip(TokenType.COLON):
            return Cell(self, start=start, key=key, value=self.parseExpression())
        else:
            return key


    def parseCell(self):
        return Cell(self,
            start = self.token.start,
            key = self.parseExpression(),
            value = self.expect(TokenType.COLON) and self.parseExpression())


    def parseExpression(self):
        token = self.token
        if token.type is TokenType.PAREN_L:
            return self.parseList()
        elif token.type is TokenType.BRACE_L:
            return self.parseObject()
        elif token.type is TokenType.INTEGER:
            return Integer(self, value=int(token.value), advance=True)
        elif token.type is TokenType.FLOAT:
            return Float(self, value=float(token.value), advance=True)
        elif token.type is TokenType.STRING:
            return String(self, value=str(token.value), advance=True)
        elif token.type is TokenType.OPERATOR:
            return Operator(self, value=token.value, advance=True)
        elif token.type is TokenType.NAME:
            return self.parseSymbol()

        raise self.unexpected()


    def parseSymbol(self):
        token = self.token
        if token.value in ('true', 'false'):
            return Boolean(self, value=(token.value == 'true'), advance=True)
        elif token.value == 'nil':
            return Nil(self, value=None, advance=True)
        else:
            return Symbol(self, value=token.value, advance=True)



    # Token checkers
    def advance(self):
        self.prev_end = self.token.end
        self.token = self.lexer.nextToken(self.prev_end)

    def peek(self, type):
        return self.token.type is type

    def skip(self, type):
        match = self.token.type is type
        if match:
            self.advance()
        return match

    def unexpected(self):
        return SyntaxError(self.source, self.token.start, 'Unexpected {}'.format(self.token.type))

    def expect(self, type):
        token = self.token
        if token.type is type:
            self.advance()
            return token
        else:
            raise SyntaxError(self.source, token.start, 'Expected {}, found {}'.format(type, token))

    def expectKeyword(self, value):
        token = self.token
        if token.type == TokenType.NAME and token.value == value:
            self.advance()
            return token
        else:
            raise SyntaxError(self.source, token.start, 'Expected "{}", found {}'.format(value, token))

    def any(self, start_type, parser, end_type):
        self.expect(start_type)
        nodes = []
        while not self.skip(end_type):
            nodes += [parser()]
        return nodes

    def many(self, start_type, parser, end_type):
        self.expect(start_type)
        nodes = [parser()]
        while not self.skip(end_type):
            nodes += [parser()]
        return nodes

    def sequence(self, test, parser):
        results = []
        while test():
            results += [parser()]
        return results
