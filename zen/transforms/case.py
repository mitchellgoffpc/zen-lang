from zen.ast import *


# Caseify transform
def caseify(node, first=False):
    if node.cls is Symbol:
        return Symbol(None, value=recase(node.value, first), loc=node.loc)
    elif node.cls is List:
        return List(None, values=[caseify(x, i == 0) for i, x in enumerate(node.values)])
    else:
        return node


# Helper functions
def recase(value, first):
    i = 0

    while i < len(value):
        if value[i] == '-':
            if first and i < len(value) - 1:
                value = value[:i] + value[i+1].upper() + value[i+2:]
            else:
                value = value[:i] + '_' + value[i+1:]
            i = 0
        i += 1

    return value
