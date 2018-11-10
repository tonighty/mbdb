# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
# -----------------------------------------------------------------------------

import sys
import ply.lex as lex
import ply.yacc as yacc

sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

reserved = {
    'create': 'CREATE',
    'table': 'TABLE',
}

tokens = [
    'IDENTIFIER',
] + list(reserved.values())

literals = [',', '(', ')']

# Tokens
t_ignore = " \t"


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lex.lex()

# Parsing rules
precedence = ()

# dictionary of names
names = {}


def p_statement_create(p):
    ''' statement : CREATE TABLE identifier columns '''
    print([i for i in p])


def p_columns(p):
    "columns : '(' list ')'"
    p[0] = p[2]


def p_list(p):
    '''list : identifier
            | list "," identifier'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = None


def p_identifier(p):
    r'identifier : IDENTIFIER'
    p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


yacc.yacc()


def main():
    while 1:
        try:
            s = raw_input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        yacc.parse(s)


main()
