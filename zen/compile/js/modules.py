import zen.ast as ast
import zen.compile.js.ast as js

from zen.library.macros.core import *


def compileImport(node, env):
    args = node.values[1:]
    imports = []
    i = 0

    while i < len(args) and not isKeyword(args[i]):
        imports.append(args[i])
        i += 1

    keywords = getKeywords(args[i:])


    # import :as
    if 'as' in keywords:
        assert len(imports) == 1
        assert keywords['as'].cls is ast.Symbol

        alias = keywords['as'].value
    else:
        alias = None


    # import :from
    if 'from' in keywords:
        path = []
        node = keywords['from']

        if node.cls is ast.String:
            path = node.value
        else:
            path = unwind(node)

        for item in imports:
            assert item.cls is ast.Symbol
            env.outermost().createImport(target=item.value, path=path, alias=alias)

    # import
    else:
        assert len(imports) == 1

        path = unwind(imports[0])
        env.outermost().createImport(target=path[-1], path=path[:-1], alias=alias)

    return js.Null(), []
