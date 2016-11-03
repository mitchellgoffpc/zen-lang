import math
import operator as op

from zen.ast import *


# Function class
class Function(object):
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env

    def __call__(self, *args):
        return eval(self.body, Env([x.value for x in self.params.values], args, self.env))

# Environment class
class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var):
        return (self if var in self
                     else self.outer.find(var))


# An environment with some Scheme standard procedures
def build_standard_env():
    env = Env()

    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.div,
        '>': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'abs':          abs,
        'append':       op.add,  
        'apply':        apply,
        'begin':        lambda *x: x[-1],
        'car':          lambda x: x[0],
        'cdr':          lambda x: x[1:], 
        'cons':         lambda x,y: [x] + y,
        'eq?':          op.is_, 
        'equal?':       op.eq, 
        'length':       len, 
        'list':         lambda *x: list(x), 
        'list?':        lambda x: isinstance(x,list), 
        'map':          map,
        'max':          max,
        'min':          min,
        'not':          op.not_,
        'null?':        lambda x: x == [], 
        'number?':      lambda x: isinstance(x, Number),   
        'procedure?':   callable,
        'round':        round,
        'symbol?':      lambda x: isinstance(x, Symbol),
        'if':           'if',
        'define':       'define',
        'quote':        'quote',
        'set':          'set',
        'lambda':       'lambda' })

    return env

global_env = build_standard_env()



# Evaluate an expression in an environment.
def eval(node, env=global_env):
    if node.cls is Symbol:            # variable reference
        return env.find(node.value)[node.value]
    elif not node.cls is List:        # constant literal
        return node.value
    else:                             # procedure call
        proc = eval(node.values[0], env)

        if proc == 'quote':
            (_, exp) = node.values
            return exp
        elif proc == 'if':
            (_, test, conseq, alt) = node.values
            exp = (conseq if eval(test, env) else alt)
            return eval(exp, env)
        elif proc == 'define': 
            (_, var, exp) = node.values
            env[var.value] = eval(exp, env)
        elif proc == 'set':
            (_, var, exp) = node.values
            env.find(var)[var] = eval(exp, env)
        elif proc == 'lambda':
            (_, params, body) = node.values
            return Function(params, body, env)
        elif not callable(proc):
            raise Exception("Error: {} is not a function".format(proc))
        else:
            args = [eval(arg, env) for arg in node.values[1:]]
            return proc(*args)
