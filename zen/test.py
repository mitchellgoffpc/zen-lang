from zen.lex import Lexer, TokenType
from zen.parse import Parser
from zen.source import Source
from zen.eval import eval

from zen.transforms.infix import resolveFixity
from zen.transforms.macros import resolve_macros
from zen.transforms.case import caseify

from zen.ast import *
from zen.compile.compile import compileExpression
from zen.compile.environment import Environment


# with open('../code.zen', 'r') as code:
#     source = Source(code.read(), 'code')
#     parser = Parser(source)

# for ast in parser.parse():
#     print ast
#     print resolveFixity(ast)
    # print eval(ast)

# cased_ast = caseify(ast)
# macro_ast = resolve_macros(infix_ast)

node = List(None, values=[
    Symbol(None, value='+'),
    String(None, value="hello"),
    Integer(None, value="hello")])

node = Integer(None, value=1)

env = Environment()

print compileExpression(node, env)
print env
