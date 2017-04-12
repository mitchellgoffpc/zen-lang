from zen.ast import *
from zen.parse.lex import butterflies

butterflies = [x for x in butterflies if x != '_']


# resolveCase transform
def resolveCase(node):
    if node.cls is Symbol:
        return Symbol(None, value=recase(node.value))
    elif node.cls is List:
        return List(None, values=[resolveCase(x) for x in node.values])
    else:
        return node


# Helper functions
def recase(value):
    i = 0

    while i < len(value):
        if value[i] in butterflies:
            value = value[:i] + '_' + value[i+1:]
            i = 0
        i += 1

    return value
