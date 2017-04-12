from zen.parse.parse import Parser
from zen.parse.source import Source

from zen.transforms.decorators import resolveDecorators
from zen.transforms.infix import resolveFixity
from zen.transforms.case import resolveCase
from zen.transforms.macros import resolveMacros

from zen.compile.js.compile import *
from zen.compile.js.environment import *
from zen.compile.js.primitives import *
from zen.compile.js.write import *


with open('code.zen', 'r') as code:
    source = Source(code.read(), 'code')
    parser = Parser(source)

nodes = list(parser.parse())
nodes = [resolveDecorators(node) for node in nodes]
nodes = [resolveFixity(node) for node in nodes]
nodes = [resolveCase(node) for node in nodes]

main = compile(nodes)
for item in main:
    print item
