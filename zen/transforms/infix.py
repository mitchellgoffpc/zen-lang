from zen.ast import *
from zen.errors import SyntaxError


# Operators
operators = {
    ',':  (1, 'left'),
    '->': (3, 'left'),
    '+': (5, 'left'),
    '-': (5, 'left'),
    '*': (6, 'left'),
    '/': (6, 'left'),
    ':': (8, 'left'),
    '.': (9, 'left') }


# Operator fixity transform
def resolveFixity(node):
    if node.cls is Cell:
        return resolveCellFixity(node)
    elif node.cls is List:
        return resolveListFixity(node)
    else:
        return node

def resolveCellFixity(node):
    return Cell(None, key=resolveFixity(node.key), value=resolveFixity(node.value))

def resolveListFixity(node):
    i, op = lookahead(node.values, 0)
    j, next_op = lookahead(node.values, i+1)

    if not op:
        return List(None, values=[resolveFixity(x) for x in node.values])
    elif not next_op:
        return infix(node.values, i)
    elif operators[op][0] > operators[next_op][0]:
        return infix(node.values, j)
    elif operators[op][0] < operators[next_op][0]:
        return infix(node.values, i)
    elif operators[op][1] == 'left':
        return infix(node.values, j)
    elif operators[op][1] == 'right':
        return infix(node.values, i)
    else:
        raise Exception('We have a problem!')


# Helper functions
def infix(list, i):
    values = [
        Symbol(None, value=list[i].value, loc=list[i].loc),
        split(list[:i]),
        split(list[i+1:])]

    return resolveFixity(List(None, values=filter(bool, values)))

def split(list):
    if len(list) == 0:
        return None
    elif len(list) == 1:
        return list[0]
    else:
        return List(None, values=list)

def lookahead(values, start):
    return next((
        (i, v.value)
        for i, v in enumerate(values)
        if v.cls is Operator and i >= start),
        (-1, None))
