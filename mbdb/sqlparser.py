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
	'update': 'UPDATE',
	'delete': 'DELETE',
	'where': 'WHERE',
	'set': 'SET',
}

tokens = [
	         'IDENTIFIER',
	         'OPERATOR',
	         'INT',
	         'STR',
         ] + list(reserved.values())

literals = [',', '(', ')', '%', '=']

# Tokens
t_ignore = " \t"

t_STR = r'\"' + r'.+?' + r'\"'

#
# def t_STR(t):
# 	r'\\".+?\\"'
# 	# t.value = t.value[1:len(t.value) - 1]
# 	# print(t.value)
# 	return t


def t_INT(t):
	r'\d+'
	try:
		t.value = int(t.value)
	except ValueError:
		raise ValueError("Integer value too large %d", t.value)
	return t


def t_IDENTIFIER(t):
	r'[a-zA-Zа-яА-Я_][a-zA-Zа-яА-Я0-9_]*|\d+|\*'
	t.type = reserved.get(t.value, 'IDENTIFIER')  # Check for reserved words
	return t


def t_OPERATOR(t):
	r'==|!=|>|>=|<|<='
	return t


def t_newline(t):
	r'\n+'
	t.lexer.lineno += t.value.count("\n")


def t_error(t):
	raise SyntaxError("Illegal character '%s'" % t.value[0])


# Build the lexer
lex.lex()

# Parsing rules
precedence = ()

# dictionary of names
names = {}


def p_statement_update(p):
	'''statement : UPDATE identifier SET update_values WHERE condition'''

	p[0] = p[1:]


def p_update_values(p):
	'''update_values : identifier '=' value
					 | update_values ',' identifier '=' value'''

	if len(p) == 4:
		p[0] = {p[1]: p[3]}
	elif isinstance(p[1], dict):
		p[1][p[3]] = p[5]
		p[0] = p[1]
	else:
		p[0] = None


def p_statement_delete(p):
	'''statement : DELETE FROM identifier WHERE condition'''

	p[0] = p[1:]


def p_condition(p):
	'''condition : identifier operator value'''

	p[0] = [p[1], p[2], p[3]]


def p_operator(p):
	r'''operator : OPERATOR'''

	p[0] = p[1]


def p_statement_select(p):
	'''statement : SELECT s_columns FROM identifier
				 | SELECT s_columns FROM identifier WHERE condition'''

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
	'''values : value
			  | values ',' value'''

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


def p_value(p):
	'''value : INT
			 | STR'''

	if isinstance(p[1], int):
		p[0] = p[1]
		return

	p[0] = p[1][1:len(p[1]) - 1]


def p_error(p):
	if p:
		raise SyntaxError("Syntax error at '%s'" % p.value)
	else:
		raise SyntaxError("Syntax error at EOF")


yacc.yacc()


def parse(statement):
	sql = yacc.parse(statement)
	return sql
