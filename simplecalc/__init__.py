# Copyright 2015-2018 Canonical Ltd.
# Copyright 2020 Facundo Batista
# All Rights Reserved

"""A simple calculator."""

import math
import re
from decimal import Decimal, getcontext

from ply import lex, yacc

__all__ = ['calc']

# some limits so we don't kill memory/cpu
MAX_FACTORIAL_INP = 100

# some available values for the expression
ALLOWED_VALUES = {
    'e': Decimal(math.e),
    'pi': Decimal(math.pi),
}

# crazy regex to match a number; this comes from the Python's Decimal code,
# adapted to support also commas
RE_NUMBER = r"""        # A numeric string consists of:
    (?=\d|\.\d|\,\d)           # starts with a number or a point/comma
    (?P<int>\d*)               # having a (possibly empty) integer part
    ((\.|\,)(?P<frac>\d*))?    # followed by an optional fractional part
    ((e|E)(?P<exp>[-+]?\d+))?  # followed by an optional exponent, or...
"""

# decimal context
deccontext = getcontext()


# the functions that user can call; with a map from the name to
# the real function and a possible limitation check
def better_log(n, base=None):
    """A log function with better default."""
    if base is None:
        r = Decimal(n).log10()
    else:
        r = Decimal(math.log(n, base))
    return r


def better_factorial(n):
    """A factorial with limit check."""
    if n > MAX_FACTORIAL_INP:
        raise OverflowError("Factorial input too big (max=%d)" % (
                            MAX_FACTORIAL_INP,))
    if int(n) != n:
        raise ValueError("factorial() only accepts integral values")
    return math.factorial(n)


def better_int(n, base=None):
    """An int converter to support n being already a number."""
    if base is None:
        r = int(n)
    else:
        r = int(str(n), base)
    return r


FUNCTIONS = {
    'abs': abs,
    'acos': math.acos,
    'acosh': math.acosh,
    'asin': math.asin,
    'asinh': math.asinh,
    'atan': math.atan,
    'atanh': math.atanh,
    'ceil': math.ceil,  # uses Decimal's dunder method
    'cos': math.cos,
    'cosh': math.cosh,
    'degrees': math.degrees,
    'distance': math.hypot,
    'exp': deccontext.exp,
    'factorial': better_factorial,
    'floor': math.floor,  # uses Decimal's dunder method
    'gamma': math.gamma,
    'hypot': math.hypot,
    'int': better_int,
    'ln': math.log,
    'log': better_log,
    'log10': math.log10,
    'log2': lambda n: better_log(n, 2),
    'pow': deccontext.power,
    'radians': math.radians,
    'round': round,
    'sin': math.sin,
    'sinh': math.sinh,
    'sqrt': deccontext.sqrt,
    'tan': math.tan,
    'tanh': math.tanh,
    'trunc': math.trunc,  # uses Decimal's dunder method
}


class _CalcLexer(object):
    """The lexer information for the calculator."""
    tokens = (
        'COMMA',
        'DIVIDE',
        'EQ',
        'FACTORIAL',
        'GT',
        'GTE',
        'LPAREN',
        'LT',
        'LTE',
        'MINUS',
        'MULT',
        'NAME',
        'NE',
        'NUMBER',
        'PLUS',
        'POW',
        'RPAREN',
    )

    # don't care about these
    t_ignore = ' \t'

    # regular expression rules for simple tokens
    t_FACTORIAL = r'\!'
    t_POW = r'\*\*'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULT = r'\*'
    t_DIVIDE = r'/'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r'\,'
    t_LT = r'\<'
    t_GT = r'\>'
    t_LTE = r'\<='
    t_GTE = r'\>='
    t_EQ = r'(===|==|=)'
    t_NE = r'(\!=|\<\>)'

    def t_NUMBER(self, t):
        """Docstring overwritten below, to have the regex in only one place."""
        m = re.match(RE_NUMBER, t.value, re.VERBOSE)
        intpart, fracpart, expart = m.group('int', 'frac', 'exp')
        if intpart:
            result = int(intpart)
        else:
            result = 0
        if fracpart:
            result += Decimal(fracpart) / 10 ** len(fracpart)
        if expart:
            result *= Decimal(10) ** int(expart)

        t.value = result
        return t

    t_NUMBER.__doc__ = RE_NUMBER

    def t_NAME(self, t):
        r'\w+'
        return t

    def t_error(self, t):
        raise ValueError("Illegal character: %r" % (t.value[0],))


class _CalcParser(object):
    """The parser for the calculator."""
    tokens = _CalcLexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULT', 'DIVIDE'),
        ('left', 'FACTORIAL', 'POW'),
        ('right', 'UPLUS', 'UMINUS'),
    )

    def __init__(self):
        self.parser = None
        self.lexer = None

    def parse(self, source_text):
        if self.lexer is None:
            self.lexer = lex.lex(module=_CalcLexer())
            self.parser = yacc.yacc(module=self, write_tables=False,
                                    debug=False)
        return self.parser.parse(source_text, lexer=self.lexer)

    def p_error(self, p):
        raise ValueError("Syntax error in input!")

    def p_result(self, p):
        'result : expression'
        p[0] = p[1]

    def p_expression_add(self, p):
        'expression : expression PLUS expression'
        p[0] = p[1] + p[3]

    def p_expression_unary_plus(self, p):
        'expression : PLUS expression %prec UPLUS'
        p[0] = p[2]

    def p_expression_subtract(self, p):
        'expression : expression MINUS expression'
        p[0] = p[1] - p[3]

    def p_expression_unary_minus(self, p):
        'expression : MINUS expression %prec UMINUS'
        p[0] = -p[2]

    def p_expression_mult(self, p):
        'expression : expression MULT expression'
        p[0] = p[1] * p[3]

    def p_term_div(self, p):
        'expression : expression DIVIDE expression'
        p[0] = p[1] / Decimal(p[3])

    def p_expression_power(self, p):
        'expression : expression POW expression'
        p[0] = p[1] ** Decimal(p[3])

    def p_expression_factorial(self, p):
        'expression : expression FACTORIAL'
        p[0] = better_factorial(p[1])

    def p_factor_num(self, p):
        'expression : NUMBER'
        p[0] = p[1]

    def p_factor_expr(self, p):
        'expression : LPAREN expression RPAREN'
        p[0] = p[2]

    def _func_calling(self, func_name, *args):
        """Generic function calling."""
        try:
            func = FUNCTIONS[func_name]
        except KeyError:
            raise ValueError("Unknown %r function" % (func_name,))
        return Decimal(func(*args))

    def p_name_function_double_commaseparated(self, p):
        'expression : NAME LPAREN expression COMMA expression RPAREN'
        p[0] = self._func_calling(p[1], p[3], p[5])

    def p_name_function_double_spaceseparated(self, p):
        'expression : NAME LPAREN expression expression RPAREN'
        p[0] = self._func_calling(p[1], p[3], p[4])

    def p_name_function(self, p):
        'expression : NAME LPAREN expression RPAREN'
        p[0] = self._func_calling(p[1], p[3])

    def p_name_function_double_commaseparated_no_paren(self, p):
        'expression : NAME expression COMMA expression'
        p[0] = self._func_calling(p[1], p[2], p[4])

    def p_name_function_double_spaceseparated_no_paren(self, p):
        'expression : NAME expression expression'
        p[0] = self._func_calling(p[1], p[2], p[3])

    def p_name_function_no_paren(self, p):
        'expression : NAME expression'
        p[0] = self._func_calling(p[1], p[2])

    def p_name_value(self, p):
        'expression : NAME'
        val_name = p[1]
        try:
            p[0] = ALLOWED_VALUES[val_name]
        except KeyError:
            raise ValueError("Unknown %r value" % (val_name,))

    def p_result_bool(self, p):
        'result : bool'
        p[0] = p[1]

    def p_comparison(self, p):
        '''bool : expression LT expression
                | expression GT expression
                | expression LTE expression
                | expression GTE expression
                | expression EQ expression
                | expression NE expression
        '''
        if p[2] == '<':
            p[0] = p[1] < p[3]
        elif p[2] == '>':
            p[0] = p[1] > p[3]
        elif p[2] == '<=':
            p[0] = p[1] <= p[3]
        elif p[2] == '>=':
            p[0] = p[1] >= p[3]
        elif p[2] in ('=', '==', '==='):
            p[0] = p[1] == p[3]
        elif p[2] in ('<>', '!='):
            p[0] = p[1] != p[3]


_cp = _CalcParser()


def calc(source):
    """Parse and calculate what's in the source text."""
    resp = _cp.parse(source.strip().lower())
    return resp


if __name__ == '__main__':
    import sys
    print(calc(" ".join(sys.argv[1:])))
