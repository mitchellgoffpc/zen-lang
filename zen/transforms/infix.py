from zen.ast import *
from zen.errors import SyntaxError

operators = {
    '->': (2, 'left'),
    '=': (3, 'left'),

    '==': (8, 'right'),
    '!=': (8, 'right'),

    '>': (9, 'right'),
    '<': (9, 'right'),
    '<=': (9, 'right'),
    '>=': (9, 'right'),

    '+': (10, 'right'),
    '-': (10, 'right'),

    '*': (11, 'right'),
    '/': (11, 'right'),
    '**': (11, 'right'),
    '%': (11, 'right'),

    '@': (14, 'left'),
    '.': (15, 'left') }



# Operator fixity transform
def resolveFixity(node):
    if node.cls is not List:
        return node

    input = node.values[::-1]
    operators = []
    output = []
    first = True

    while input:
        next = input.pop()
        next = resolveFixity(next)

        if next.cls is not Operator:
            output.append(next)
        elif first:
            output.append(next)
        else:
            while operators and \
                  ((assoc(next) == 'left' and
                    precedence(next) <= precedence(operators[-1])) or
                   (assoc(next) == 'right' and
                    precedence(next) < precedence(operators[-1]))):
                output.append(List(None, values=[output.pop(), output.pop(), operators.pop()][::-1]))

            operators.append(next)

        first = False

    while operators:
        output.append(List(None, values=[output.pop(), output.pop(), operators.pop()][::-1]))

    return List(None, values=output)



# Helper functions
def assoc(op):
    _, assoc = operators.get(op.value, (None, None))
    return assoc

def precedence(op):
    precedence, _ = operators.get(op.value, (None, None))
    return precedence
