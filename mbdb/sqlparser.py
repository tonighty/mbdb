import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'create': 'CREATE',
    'table': 'TABLE',
    'database': 'DATABASE',
    'show': 'SHOW',
    'number': 'NUMBER',
    'string': 'STRING',
    'insert': 'INSERT',
    'into': 'INTO',
    'values': 'VALUES',
    'select': 'SELECT',
    'from': 'FROM',
    '*': 'ALL',
}

tokens = [
             'IDENTIFIER',
         ] + list(reserved.values())

literals = [',', '(', ')', '%']

# Tokens
t_ignore = " \t"


def t_IDENTIFIER(t):
    r'[a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]*|\d+|\*'
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


def p_statement_select(p):
    '''statement : SELECT s_columns FROM identifier
                 | SELECT ALL FROM identifier'''

    p[0] = p[1:]


def p_s_columns(p):
    '''s_columns : identifier
                 | s_columns ',' identifier'''

    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = None


def p_statement_insert(p):
    '''statement : INSERT INTO identifier VALUES '(' values ')' '''

    p[0] = p[1:]


def p_statement_values(p):
    '''values : identifier
              | values ',' identifier'''

    if len(p) == 2:
        p[0] = [p[1]]
    elif isinstance(p[1], list):
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = None


def p_statement_create_table(p):
    '''statement : CREATE TABLE identifier columns'''

    p[0] = p[1:]


def p_statement_show_create_table(p):
    '''statement : SHOW CREATE TABLE identifier'''

    p[0] = p[1:]


def p_statement_create_db(p):
    '''statement : CREATE DATABASE identifier'''

    p[0] = p[1:]


def p_columns(p):
    "columns : '(' list ')'"
    p[0] = p[2]


def p_list(p):
    '''list : identifier type
            | list "," identifier type'''
    if len(p) == 3:
        p[0] = [{'name': p[1], 'type': p[2]}]
    elif isinstance(p[1], list):
        p[1].append({'name': p[3], 'type': p[4]})
        p[0] = p[1]
    else:
        p[0] = None


def p_identifier(p):
    r'''identifier : IDENTIFIER'''
    p[0] = p[1]


def p_type(p):
    '''type : NUMBER
            | STRING'''
    p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


yacc.yacc()


def parse(statement):
    sql = yacc.parse(statement)
    return sql
