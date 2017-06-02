import zen.ast as ast
import zen.compile.js.ast as js

from zen.compile.js.util import *


# Compile an import statement
def compileImport(node, env):
    args = node.values[1:]
    imports = []
    i = 0

    while i < len(args) and not isKeyword(args[i]):
        assert args[i].cls is ast.Symbol
        imports.append(args[i].value)
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
        assert keywords['from'].cls is ast.Symbol

        if alias:
            assert len(imports) == 1

        for target in imports:
            env.outermost().createImport(
                target = target,
                ns = keywords['from'].value,
                alias = alias)

    # import
    else:
        assert len(imports) == 1

        env.outermost().createImport(
            target = None,
            ns = imports[0],
            alias = alias)

    return []
