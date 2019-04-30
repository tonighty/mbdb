import json
import os
import pickle
import shutil
import socket
import tempfile

from mbdb.sqlparser import parse

DEFAULT_DB_PATH = tempfile.mkdtemp()


class mbdb:

	def __init__(self, name, path = DEFAULT_DB_PATH, type = 'local', host = '127.0.0.1', port = 65432):
		self._db_name = name
		self.type = type

		if type == 'client':
			self.host = host
			self.port = port
			return

		self._db_path = path
		if not os.path.exists(self._db_path):
			os.mkdir(self._db_path)

		self._meta_path = os.path.join(self._db_path, self._db_name, '_META.json')
		self._create_database()

		self._is_transaction = False
		self._temp_tables = {}

	def get_database_path(self):
		return self._db_path

	def begin_transaction(self):
		self._is_transaction = True

	def commit(self):
		if not self._is_transaction:
			return

		for name, path in self._temp_tables.items():
			os.remove(path)
			os.replace(path, self._get_table_path(name, False, False))
		self._is_transaction = False

	def exec(self, statement):
		if self.type == 'client':
			return self._send_socket(statement)

		self._check_for_db()

		sql = parse(statement)

		if sql is None:
			return

		if sql[0] == 'create':
			return self._create_table(sql[2], sql[3])

		elif sql[0] == 'show':
			return self._show_create_table(sql[3])

		elif sql[0] == 'insert':
			return self._insert_into_table(sql[2], sql[5])

		elif sql[0] == 'select':
			condition = None
			if len(sql) == 6:
				condition = sql[5]
			return self._select_from_table(sql[3], sql[1], condition)

		elif sql[0] == 'delete':
			return self._delete_from_table(sql[2], sql[4])

		elif sql[0] == 'update':
			return self._update_table(sql[1], sql[3], sql[5])

	def _check_for_db(self):
		if not self._db_name:
			return self._handle_error(Exception('Database does not exist'))

	def _is_legal_table(self, name):
		data = self._read_meta()
		for table in data:
			if table['table_name'] == name:
				return True

		return False

	def _check_table_readability(self, name):
		if not self._is_legal_table(name):
			return self._handle_error(Exception('Table does not exists'))

		if not self._is_legal_file(self._get_table_path(name)):
			return None

	def _get_table_path(self, name, is_changed = False, original = True):
		if self._is_transaction and not original:
			if name in self._temp_tables:
				return self._temp_tables[name]
			elif is_changed:
				self._temp_tables[name] = os.path.join(tempfile.gettempdir(), name)
				open(self._temp_tables[name], 'w').close()
				return self._temp_tables[name]
		return os.path.join(self._db_path, self._db_name, name + '.json')

	def _read_json(self, path):
		if self._is_legal_file(path):
			with open(path, 'r') as file:
				return json.load(file)
		return []

	def _read_meta(self):
		return self._read_json(self._meta_path)

	def _read_table(self, name):
		return self._read_json(self._get_table_path(name))

	def _check_column(self, name, column):
		if column is None or column == '*':
			return

		data = self._read_meta()
		for table in data:
			if table['table_name'] == name:
				for field in table['columns']:
					if field['name'] == column:
						return

		return self._handle_error(Exception('Column "%s" does not exists in "%s"' % (column, name)))

	@staticmethod
	def _is_legal_file(path):
		return os.path.exists(path) and os.path.getsize(path) > 0

	def _create_database(self):
		path = os.path.join(self._db_path, self._db_name)
		if not os.path.exists(path):
			os.mkdir(path)

	def _create_table(self, name, fields):
		data = self._read_meta()

		for table in data:
			if table['table_name'] == name:
				return self._handle_error(Exception('Table already exists'))

		new_data = {
			'table_name': name,
			'columns': fields,
		}

		with open(self._meta_path, 'w') as meta_file:
			if isinstance(data, list):
				data.append(new_data)
				json.dump(data, meta_file)
			else:
				json.dump([new_data], meta_file)

		path_table = self._get_table_path(name)
		open(path_table, 'w').close()

	def _show_create_table(self, name):
		data = self._read_meta()

		for table in data:
			if table['table_name'] == name:
				return str('create table ' + name + ' (' + ', '.join(
					[' '.join(list(i.values())) for i in table['columns']]) + ')')

		return self._handle_error(Exception('Table does not exists'))

	def _insert_into_table(self, name, fields):
		data_structure = None
		data = self._read_meta()
		for table in data:
			if table['table_name'] == name:
				data_structure = table['columns']

		if data_structure is None:
			return self._handle_error(Exception('Table does not exists'))

		table_data = self._read_table(name)

		new_data = {}
		for index, item in enumerate(data_structure):
			if list(item.values())[1] == 'number':
				fields[index] = int(fields[index])
			new_data.update({list(item.values())[0]: fields[index]})

		table_path = self._get_table_path(name, True)
		with open(table_path, 'w') as table_file:
			if isinstance(table_data, list):
				table_data.append(new_data)
				json.dump(table_data, table_file, ensure_ascii = False)
			else:
				json.dump([new_data], table_file, ensure_ascii = False)

	def _select_from_table(self, name, columns, condition = None):
		self._check_table_readability(name)

		if condition is not None:
			self._check_column(name, condition[0])

		for column in columns:
			self._check_column(name, column)

		data = self._read_table(name)

		if columns[0] == '*':
			return data

		result = []
		for row in data:
			row_res = {}
			for column in columns:
				val = row.get(column)
				if val and (condition is None or condition[0] == column and self._handle_condition(val, condition[1], condition[2])):
					row_res[column] = val
			if row_res != {}:
				result.append(row_res)

		return result

	def _delete_from_table(self, name, condition):
		self._check_table_readability(name)

		if condition is not None:
			self._check_column(name, condition[0])

		data = self._read_table(name)

		table_path = self._get_table_path(name, True)
		with open(table_path, 'w') as table_file:
			column = condition[0]
			operator = condition[1]
			value = condition[2]

			for item in data:
				if self._handle_condition(item[column], operator, value):
					del item[column]

			json.dump(data, table_file, ensure_ascii = False)

	def _update_table(self, name, values, condition):
		self._check_table_readability(name)

		if condition is not None:
			self._check_column(name, condition[0])

		data = self._read_table(name)

		table_path = self._get_table_path(name, True)
		with open(table_path, 'w') as table_file:
			column = condition[0]
			operator = condition[1]
			value = condition[2]

			for row in data:
				if self._handle_condition(row[column], operator, value):
					for column in row:
						if values[column]:
							row[column] = type(row[column])(values[column])

			json.dump(data, table_file, ensure_ascii = False)

	def _handle_error(self, exception):
		self._is_transaction = False
		
		if self.type == 'server':
			return exception
		
		raise exception

	def _handle_condition(self, value1, operator, value2):
		try:
			if operator == '==':
				return value1 == type(value1)(value2)

			elif operator == '!=':
				return value1 != type(value1)(value2)

			elif operator == '>':
				return value1 > type(value1)(value2)

			elif operator == '>=':
				return value1 >= type(value1)(value2)

			elif operator == '<':
				return value1 < type(value1)(value2)

			elif operator == '<=':
				return value1 <= type(value1)(value2)
		except ValueError:
			return self._handle_error(ValueError('"%s" must be type of "%s"' % (value2, type(value1))))

	def _send_socket(self, statement):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.connect((self.host, self.port))
			s.sendall(statement.encode())
			return pickle.loads(s.recv(1024))
