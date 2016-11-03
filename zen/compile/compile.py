from zen.ast import *
from zen.compile.types import *
from zen.compile.environment import *


# Primitive functions
# infix_operators = ('+', '-', '*', '/', '%', '&', '&&', '|', '||',
#                    '=', '==', '<', '<=', '>', '>=')
# prefix_operators = ('!', '~', '&')

# infix_operators = { ('+', IntType, IntType): '+',
#                     ('-', IntType, IntType): '-' }

# func_primitives = { ('+', StringType, StringType): 'strcat' }
# special_forms = ('if', 'do')

# primitives = dict(infix_operators, func_primitives)



# Compile
def compile(list, env):
    results = []

    for node in list:
        results += [_compile(node)]

    main = FunctionDeclaration(
        Int,
        'main',
        [ FunctionArg(IntegerType(), 'argc'),
          FunctionArg(PointerType(PointerType(CharType())), 'argv') ],
        [ x for x in results
            if isinstance(x, Expression) ])

    return '\n\n'.join(
        x.compile()
        for x in results + [main]
        if isinstance(x, FunctionDeclaration))
    

def compileBlock(nodes):
    return Block([compileExpression(expr) for expr in nodes])


def compileExpression(node):
    if node.cls in (Integer, Float, Symbol):
        return Literal(node.value)
    elif node.cls is List:
        if len(node.values) == 0:
            raise Exception("Empty lists cannot be evaluated")
        
        f = node.values[0].value

        if f == 'func':
            (_, name, args), body = node.values[:3], node.values[3:]
            return FunctionDeclaration(
                IntegerType(),
                name,
                [FunctionArg(IntegerType(), arg) for arg in args.values],
                compileBlock(body))

        elif f == 'return':
            return FunctionReturn(compileExpression(node.values[1]))

        elif f == 'default':
            return Literal(1)

        elif f == 'if':
            _, cond, expr, alt = node.values
            return TernaryOperator(
                compileExpression(cond),
                compileExpression(expr),
                compileExpression(alt))

        elif f == 'switch':
            pass

        elif f == 'cond':
            cases = [x.values for x in node.values[1:]]
            ifs = [
                IfStatement(
                    compileExpression(x.values[0]),
                    compileBlock(x.values[1:]))
                for x in node.values[1:]]

            return IfElseStatement(ifs)

        elif f in infix_operators:
            return InfixOperator(f,
                compileExpression(node.values[1]),
                compileExpression(node.values[2]))

        elif f == 'not':
            return PrefixOperator('!', compileExpression(node.values[1]))

        else:
            return FunctionCall(f, [compileExpression(x) for x in node.values[1:]])



def compileExpression(node, env):
    if node.cls is List:
        return compileFunctionCall(node, env)
    elif node.cls is Symbol:
        return env.find(node.value)
    elif node.cls is String:
        return env.generate(StringType, node.value)
    elif node.cls is Integer:
        return IntLiteral(node.value)
    elif node.cls is Float:
        return FloatLiteral(node.value)
    else:
        raise CompileError('Unexpected node - {}'.format(node))



# Compile a function call (i.e. evaluate an unquoted list)
def compileFunctionCall(node, env):
    if node.cls is not List or len(node.values) == 0:
        raise CompileError('`{}` is not a function call'.format(node))

    f_sym = node.values[0].value
    args, kwargs = [], {}

    # Make a list of all the arguments that get passed
    for arg_node in node.values[1:]:
        if arg_node.cls is Cell:
            if arg_node.key.cls is not Symbol:
                raise SyntaxError("'{}' is not a valid keyword for " +
                                  "a function call".format(arg_node.key))
            else:
                kwargs[arg_node.key.value] = arg_node.value
        elif len(kwargs) > 0:
            raise SyntaxError("non-keyword arg after a keyword arg")
        else:
            args.append(arg_node)


    # Check if `f` is a special form
    if f_sym in primitives:
        return compilePrimitive(f_sym, args, env)

    # If not, match `f`'s type signiture against `type`
    f = env.find(f_sym, node)

    if not isinstance(f, FunctionType):
        raise CompileError("`{}` is not a function".format(f_sym))
    elif type is not None:
        if f.returns is None:
            env.setType(f, type, node)
        elif not type.accepts(f.returns):
            raise CompileError("function ({} ...) has return type `{}` " +
                               "(expected {})".format(f_sym, f.returns, type))

    # Then match `f`'s type signiture against `args` and `kwargs`
    for i, arg in enumerate(args):
        f_arg = f.args[i]
        if not f_arg.type.accepts(arg):
            raise CompileError("argument '{}' expects type '{}' but received " +
                               "type '{}'".format(f_arg.name, f_arg.type, arg.type))

        

    # If everything checks out, compile into a function call
    return FunctionCall(f, args, node)



# Compile special forms
def compilePrimitive(f, args, env):
    if f in (f for f, _, _ in infix_operators):
        return InfixOperator(f, [compileExpression(arg, env) for arg in args])
    elif f == 'if':
        return compileIfForm(args, env)
    elif f == 'do':
        return compileDoForm(args, env)



def compileIfForm(node, env):
    if len(node.values) == 3:
        _, cond, then = node.values
        return compileIfStatement(compileExpression(cond, Boolean),
                                  compileBlock(then))
    elif len(node.values) == 4:
        _, cond, then, alt = node.values
        return compileIfElseStatement(compileExpression(cond, Boolean),
                                      compileBlock(then),
                                      compileBlock(alt))
    else:
        raise ArgumentError('if', len(node.values) - 1, 2, 3)


def compileIfStatement(node, env):
    pass


def compileDoStatement(node, env):
    if len(node.values) < 2:
        raise ArgumentError('do', len(node.values) - 1, 1)

    return compileBlock(none, env)

def compileBlock(nodes, env):
    results = []
    for node in nodes:
        results += compileStatement(node)



# Helper functions
def setDependency(env, container, value):
    if container.type is None:
        pass
    elif value.type is None:
        env.setType(f, type, node)
    elif not type.accepts(f.returns):
            raise CompileError("function ({} ...) has return type `{}` " +
                               "(expected {})".format(f_sym, f.returns, type))

def split(list, f):
    a, b = [], []
    
    for x in list:
        if f(x):
            a.append(x)
        else:
            b.append(x)

    return a, b
