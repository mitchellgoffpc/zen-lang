import zen.ast as ast
import zen.compile.js.ast as js


# A whole bunch of utility functions!

# TODO: Document all this stuff

def JSObject(**kwargs):
    return js.Object(values=[
        (js.String(value=key), value)
        for key, value in kwargs.items()])


def keyword(name):
    return ast.List(None, values=[
        ast.Symbol(None, value='keyword'),
        ast.Symbol(None, value=name)])

def getKeywords(args):
    i = 0
    results = {}

    while i < len(args) and isKeyword(args[i]):
        results[args[i].values[1].value] = args[i+1]
        i += 2

    return results

def isKeyword(node):
    return (
        node.cls is ast.List and
        len(node.values) == 2 and
        node.values[0].cls is ast.Symbol and
        node.values[0].value == 'keyword' and
        node.values[1].cls in (ast.Symbol, ast.Boolean, ast.Nil))

def getSelector(args):
    return ''.join(
        ':{}'.format(x.values[1])
        for x in args
        if isKeyword(x))

def unwind(node):
    result = []

    while (node.cls is ast.List and
           len(node.values) == 3 and
           node.values[0].cls is ast.Operator and
           node.values[0].value is '.' and
           node.values[2].cls is ast.Symbol):

        result.append(node.values[2].value)
        node = node.values[1]

    assert node.cls is ast.Symbol
    return list(reversed([node.value] + result))
