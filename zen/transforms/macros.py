from zen.ast import *
from zen.library.macros.core import *


# Macros
macros = {
    'def': defFunction,
    'class': defClass,
    'comment': lambda *args: None,
    '->': lambda a, b: List(None, values=[Symbol(None, value="lambda"), a, b]),
    '=': lambda a, b: List(None, values=[Symbol(None, value="set"), a, b]) }


# Macro resolution transform
def resolveMacros(node):
    if (node.cls is List and
        len(node.values) > 0 and
        node.values[0].cls is Symbol and
        node.values[0].value in macros):
        return macros[node.values[0].value](*node.values[1:])
    elif node.cls is List:
        return List(None, values=filter(None, [resolveMacros(x) for x in node.values]))
    else:
        return node
