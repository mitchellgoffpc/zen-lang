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
        List(None, values=[Symbol(None, value='lambda'), args] + list(body))])


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

def getSelector(args):
    return ''.join(
        ':{}'.format(x.values[1].value)
        for x in args
        if isKeyword(x))

def unwind(node):
    result = []

    while (node.cls is List and
           len(node.values) == 3 and
           node.values[0].cls is Operator and
           node.values[0].value is '.' and
           node.values[2].cls is Symbol):

        result.append(node.values[2].value)
        node = node.values[1]

    assert node.cls is Symbol
    return list(reversed([node.value] + result))

def unpack(source, dest):
    results = []
    i = 0

    while i < len(source) and i < len(dest):
        if (dest.values[i].cls is Operator and
            dest.values[i].value is '&'):

            assert len(dest.values) == i + 2
            results += [(dest.values[i+1], List(None,
                values = [Symbol(None, value='tuple')] + source.values[i:]))]

        else:
            results += [(dest.values[i], source.values[i])]

        i += 1

    return List(None, values=[
        Symbol(None, value='do'),
        List(None, values=[
            List(None, values=[Operator(None, value='='), x, y])
            for x, y in results])])
