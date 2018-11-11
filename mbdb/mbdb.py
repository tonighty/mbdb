# -----------------------------------------------------------------------------
# calc.py
#
# A simple calculator with variables.   This is from O'Reilly's
# "Lex and Yacc", p. 63.
# -----------------------------------------------------------------------------
import json
import os
import sys
import ply.lex as lex
import ply.yacc as yacc

sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

reserved = {
    'create': 'CREATE',
    'table': 'TABLE',
    'database': 'DATABASE',
    'show': 'SHOW',
    'number': 'NUMBER',
    'string': 'STRING',
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

DEFAULT_DB_PATH = 'C:\mbdb'
ACTIVE_DB = 'hui'

print('Your databases are located in ', DEFAULT_DB_PATH)
print('Would you like to change it? (y/n)')
if input() != 'n':
    print('Input your new DBs location:')
    path = input()
    if not os.path.exists(path):
        os.mkdir(input())
else:
    if not os.path.exists(DEFAULT_DB_PATH):
        os.mkdir(DEFAULT_DB_PATH)


def p_statement_create_table(p):
    '''statement : CREATE TABLE identifier columns'''

    print([i for i in p])
    if not ACTIVE_DB:
        print('First open or create database')
    else:
        path_meta = DEFAULT_DB_PATH + '\\' + ACTIVE_DB + '\\_META.json'
        data = None
        if os.path.exists(path_meta):
            try:
                data = json.load(open(path_meta, 'r'))
                for table in data:
                    if table['table_name'] == p[3]:
                        print('Table already exists')
                        return 1
            except json.JSONDecodeError:
                print('Database is empty')
        new_data = {
            'table_name': p[3],
            'columns': p[4],
        }
        with open(path_meta, 'w') as metafile:
            if isinstance(data, list):
                data.append(new_data)
                json.dump(data, metafile)
            else:
                json.dump([new_data], metafile)


def p_statement_show_create_table(p):
    '''statement : SHOW CREATE TABLE identifier'''

    print([i for i in p])
    if not ACTIVE_DB:
        print('First open or create database')
    else:
        path_meta = DEFAULT_DB_PATH + '\\' + ACTIVE_DB  + '\\_META.json'
        data = json.load(open(path_meta, 'r'))
        for table in data:
            if table['table_name'] == p[4]:
                print('create table ' + p[4] + ' (' + ', '.join([' '.join(list(i.values())) for i in table['columns']]) + ')')


def p_statement_create_db(p):
    '''statement : CREATE DATABASE identifier'''

    print([i for i in p])
    path = DEFAULT_DB_PATH + '\\' + p[3]
    if not os.path.exists(path):
        os.mkdir(path)
    else:
        print('Database already exists')

    print('Open it now? (y/n)')
    if input() != 'n':
        global ACTIVE_DB
        ACTIVE_DB = p[3]


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


def main():
    while 1:
        try:
            s = raw_input('query > ')
        except EOFError:
            break
        if not s:
            continue
        yacc.parse(s)


main()
