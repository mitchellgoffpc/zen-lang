from zen.ast import *

from zen.compile.js.util import isKeyword


def resolveDecorators(node):
    if node.__class__ is list:
        raise

    if node.cls not in (List, Array, Map):
        return node

    i = 0
    while i < len(node.values):
        child = node.values[i]

        try:
            if child.cls is Operator and child.value in decorators:
                node = decorators[child.value](node, i)
        except:
            for child in node.values:
                print child
            raise

        i += 1

    if node.cls is List:
        return List(None, values=[resolveDecorators(child) for child in node.values])
    elif node.cls is Array:
        return List(None, values=(
            [Symbol(None, value='Array')] +
            [resolveDecorators(child) for child in node.values]))
    elif node.cls is Map:
        children = [resolveDecorators(child) for child in node.values]
        children = [List(None, values=[x]) if isKeyword(x) else x for x in children]
        return List(None, values=[Symbol(None, value='Map')] + children)



# Postfix decorators
def call(node, i):
    return postfix(node, i, 'call')


# Prefix decorators
def quote(node, i):
    return prefix(node, i, 'quote')

def unquote(node, i):
    return prefix(node, i, 'unquote')

def keyword(node, i):
    return prefix(node, i, 'keyword')

def escape(node, i):
    return prefix(node, i, 'escape')

def special(node, i):
    if i >= len(node.values) - 1:
        raise Exception("Invalid decorator")

    op = node.values[i + 1]
    if op.cls is Map:
        return substitute(node, i, i+2, List(None, values=(
            [Symbol(None, value='Set')] +
            node.values[i + 1].values)))

    elif op.cls is String:
        return substitute(node, i, i+2, List(None, values=[
            Symbol(None, value='regexp'),
            node.values[i + 1]]))

    else:
        raise Exception()



# Helper functions
def substitute(node, start, end, child):
    return node.cls(None, values=node.values[:start] + [child] + node.values[end:])

def prefix(node, i, symbol):
    if i >= len(node.values) - 1:
        raise Exception("Invalid position for prefix decorator")

    return substitute(node, i, i+2, List(None, values=[
        Symbol(None, value=symbol),
        node.values[i + 1]]))

def postfix(node, i, symbol):
    if i == 0:
        raise Exception("Invalid position for postfix decorator")

    return substitute(node, i-1, i+1, List(None, values=[
        Symbol(None, value=symbol),
        node.values[i - 1]]))



# Decorator table
decorators = {
    '!': call,
    '\'': quote,
    '~': unquote,
    ':': keyword,
    '#': special }
