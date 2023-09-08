"""
Simple interpreter for the Scheme programming language written in python
Source: https://norvig.com/lispy.html
"""

import math
import sys
import operator as op

Symbol = str              # A tlil Symbol is implemented as a Python str
Number = (int, float)     # A tlil Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A tlil Atom is a Symbol or Number
List   = list             # A tlil List is implemented as a Python list
Exp    = (Atom, List)     # A tlil expression is an Atom or List
Env    = dict             # A tlil environment (defined below) is a mapping of {variable: value}

def standard_env() -> Env:
    "An environment with some standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        'add':      op.add,
        'sub':      op.sub,
        'mul':      op.mul,
        'div':      op.truediv, 
        '>':        op.gt,
        '<':        op.lt,
        '>=':       op.ge,
        '<=':       op.le,
        '=':        op.eq, 
        'append':   op.add,  
        'begin':    lambda *x: x[-1],
        'fst':      lambda x: x[0],
        'cons':     lambda x,y: [x] + y,
        'eq?':      op.is_, 
        'power':    pow,
        'length':   len, 
        'list':     lambda *x: List(x), 
        'max':      max,
        'min':      min,
        'not':      op.not_,
        'null?':    lambda x: x == [], 
        'number?':  lambda x: isinstance(x, Number),  
		'print':    print,
        'procedure?':callable,
        'round':    round,
        'symbol?':  lambda x: isinstance(x, Symbol),
    })
    return env

class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    "A user-defined procedure."
    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env
    def __call__(self, *args): 
        return eval(self.body, Env(self.parms, args, self.env))

global_env = standard_env()

def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

def parse(program: str) -> Exp:
    "Read an expression from a string."
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')': 
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

def eval(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):    # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):# constant 
        return x   
    op, *args = x 

    if (args[0] == '->'):       # lambda expression
        x[0], x[1] = x[1], x[0]
        return eval(x, env)

    if op == 'quote':            # quotation
        return args[0]
    elif op == 'if':             # conditional
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':         # definition
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':           # assignment
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == '->':             # procedure
        (parms, body) = args
        return Procedure(parms, body, env)
    else:                        # procedure call
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)

def read_program_from_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read().replace('\n', ' ')
            return data
    except FileNotFoundError:
        print("\"{}\" : No such file or directory".format(filename))
        sys.exit()

def main():
    # program = "(begin (define y 6) (if (> y 5) 1 0))"
    # program = "(begin (define r 2) (mul pi (mul r r)))"
    # program = "(add 6 1)"
    # program = "(power 2 8)"
    # program = "(cons 0 (list 1 2))"
    # program = "(append (list 0) (list 1 2))"
    # program = "(max 1 4)"

    if (len(sys.argv) != 2):
        print("Usage: main.py filename")
        sys.exit()

    program = read_program_from_file(sys.argv[1])

    print(eval(parse(program)))

if __name__ == "__main__":
    main()
