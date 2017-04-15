"""
Provides some core macros for the Zen language
"""

from zen.ast import *


# Core macros
def defFunction(name, args, *body):
    if name.cls is not Symbol:
        raise Exception()
    if args.cls is not List:
        raise Exception()

    return List(None, values=[
        Symbol(None, value='var'),
        name,
        List(None, values=[
            Symbol(None, value='lambda'),
            args,
            List(None, values=[Symbol(None, value='do')] + list(body))])])


def defClass(name, *args):
    if name.cls is not Symbol:
        raise Exception()

    keywords = getKeywords(args)
    properties = []
    methods = []

    for arg in args[len(keywords) * 2:]:
        if (arg.cls is List and
            len(arg.values) > 2 and
            arg.values[0].cls is Symbol):

            if (arg.values[0].value == 'def' and
                arg.values[1].cls is List):

                methods.append(List(None, values=(
                    [Symbol(None, value='def-method')] + arg.values[1:])))

            elif arg.values[0].value == 'var':
                properties.append(arg)

    return List(None, values=[
        Symbol(None, value='def-class'),
        name,
        keyword('properties'), List(None, values=properties),
        keyword('methods'), List(None, values=methods)] +
        [x for k, v in keywords.items() for x in (keyword(k), v)])



# Helper functions
def keyword(name):
    return List(None, values=[
        Symbol(None, value='keyword'),
        Symbol(None, value=name)])

def getKeywords(args):
    i = 0
    results = {}

    while i < len(args) and isKeyword(args[i]):
        results[args[i].values[1].value] = args[i+1]
        i += 2

    return results

def isKeyword(node):
    return (
        node.cls is List and
        len(node.values) == 2 and
        node.values[0].cls is Symbol and
        node.values[0].value == 'keyword' and
        node.values[1].cls is Symbol)

def unwind(node):
    result = []

    while (node.cls is List and
           len(node.values) == 3 and
           node.values[0].cls is Operator and
           node.values[0].value is '.' and
           node.values[1].cls is Symbol):

        result.append(node.values[1].value)
        node = node.values[2]

    assert node.cls is Symbol
    return result + [node.value]