"""
Write the transformed AST to C code.
"""

def writeType(node):
    if node[0] == 'INT':
        return 'int'
    elif node[0] == 'FLOAT':
        return 'float'
    elif node[0] == 'CHAR':
        return 'char'
    elif node[0] == 'POINTER':
        return '{}*'.format(writeType(node[1]))
    elif node[0] == 'FUN':
        return '{} (*{})({})'.format(
            node)

def writeExpression(node):
    return dispatch[node[0]](node)

def writeBlock(nodes, env=None):
    environment = env.write()
    expressions = [writeExpression(node) + ';' for node in nodes]

    lines = ['\t{}'.format(x) for x in '\n'.join(environment + expressions).split('\n')]
    return '{{\n{}\n}}'.format('\n'.join(lines))



def writeSymbol(node):
    _, value = node
    return str(value)

def writeOperator(node):
    _, op, left, right = node
    return '({}) {} ({})'.format(writeExpression(left), op, writeExpression(right))

def writeAssign(node):
    _, symbol, value = node
    return '{} = {}'.format(symbol, writeExpression(value))

def writeReturn(node):
    _, expr = node
    return 'return {}'.format(writeExpression(expr))

def writeCall(node):
    _, symbol, args = node
    args = ', '.join(writeExpression(arg) for arg in args)
    return '{}({})'.format(symbol, args)

def writeIfElse(node):
    _, cond, then, alt = node
    return 'if ({}) {} else {}'.format(
        writeExpression(cond),
        writeBlock(then),
        writeBlock(alt))

def writeFunction(node):
    _, env, name, type, args, body = node
    args = ', '.join('{} {}'.format(writeType(t), x) for _, x, t in args)
    return '{} {}({}) {}'.format(writeType(type), name, args, writeBlock(body, env))



dispatch = { 'INT': writeSymbol,
             'SYMBOL': writeSymbol,
             'ASSIGN': writeAssign,
             'RETURN': writeReturn,
             'OPERATOR': writeOperator, 
             'CALL': writeCall,
             'IF-ELSE': writeIfElse }
