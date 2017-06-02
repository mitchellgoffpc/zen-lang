from zen.ast import *

skips = ['def-operator', 'def-macro']

operators = {
    '|': (2, 'right'),
    '->': (3, 'left'),
    '=': (4, 'left'),

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
    'apply': (15, 'right'),
    '.': (16, 'left') }



# Shunting yard algorithm

# This is a modified version of Djaikstra's shunting yard algorithm. It takes a
# list of atoms and operators, and outputs an unambiguous AST, with all of the
# infix operators transformed into ordinary functions in the appropriate order
# of precedence.

# Note: One unusual feature of Zen is that `.` has the highest precedence of any
# operator, even higher than function application (a space). Although this is
# a little weird, it makes the language significantly less clunky to write in.

def resolveFixity(node):
    if (node.cls is not List or
        len(node.values) <= 1):
        return node

    assert node.values[-1].cls is not Operator

    # Skip special forms, like `operator`
    if (node.values[0].cls is Symbol and
        node.values[0].value in skips):
        return List(None, values=[resolveFixity(x) for x in node.values])

    input = node.values[::-1]
    operators = []
    output = []
    atom = True
    first = True

    while input:
        next = input.pop()
        next = resolveFixity(next)

        if first:
            output.append(next)

        elif next.cls is Operator or atom:
            if next.cls is not Operator:
                input.append(next)
                next = Operator(None, value='apply')

            while operators and \
                  ((assoc(next) == 'left' and
                    precedence(next) <= precedence(operators[-1])) or
                   (assoc(next) == 'right' and
                    precedence(next) < precedence(operators[-1]))):

                shunt(output, operators)

            operators.append(next)
            atom = False

        else:
            output.append(next)
            atom = True

        first = False

    while operators:
        shunt(output, operators)

    if len(output) == 1 and output[0].cls is List:
        return output[0]
    else:
        return List(None, values=output)



# Helper functions
def shunt(output, operators):
    b, a = output.pop(), output.pop()
    op = operators.pop()

    if op.value == 'apply':
        args = [a, b]

        while operators and operators[-1].value == 'apply':
            operators.pop()
            args = [output.pop()] + args

        output.append(List(None, values=args))

    else:
        output.append(List(None, values=[op, a, b]))

def assoc(op):
    _, assoc = operators.get(op.value, (None, None))
    return assoc

def precedence(op):
    precedence, _ = operators.get(op.value, (None, None))
    return precedence
