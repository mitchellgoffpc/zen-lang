from zen.lex import Lexer, TokenType
from zen.parse import Parser
from zen.source import Source
from zen.eval import eval

from zen.transforms.infix import resolveFixity
from zen.transforms.macros import resolve_macros
from zen.transforms.case import caseify

from zen.ast import *
from zen.compile.compile import *
from zen.compile.environment import *
from zen.compile.primitives import *
from zen.compile.write import *


with open('../code.zen', 'r') as code:
    source = Source(code.read(), 'code')
    parser = Parser(source)

env = GlobalEnvironment()
env.include('printf', ['FUNC', 'NIL', 'STRING'])

nodes = []
for ast in parser.parse():
    node = resolveFixity(ast)
    nodes += [node]

main = compile(nodes, env)

for line in env.write():
    print line

print writeFunction(main)

# cased_ast = caseify(ast)
# macro_ast = resolve_macros(infix_ast)
