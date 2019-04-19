import json
import os
import sys
from mbdb.sqlparser import parse

sys.path.insert(0, "../..")

DEFAULT_DB_PATH = os.path.join('mbdb-db')


class mbdb():

    def __init__(self, name, path=DEFAULT_DB_PATH):

        self._db_path = path
        if not os.path.exists(self._db_path):
            os.mkdir(self._db_path)

        self._db_name = name
        self._meta_path = os.path.join(self._db_path, self._db_name, '_META.json')
        self._create_database()

    def get_database_path(self):
        return self._db_path

    def exec(self, statement):
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
            raise Exception('Database does not exist')

    def _is_legal_table(self, name):
        if self._is_legal_file(self._meta_path):
            with open(self._meta_path, 'r') as meta_file:
                data = json.load(meta_file)
            for table in data:
                if table['table_name'] == name:
                    return True

        return False

    def _get_table_path(self, name):
        return os.path.join(self._db_path, self._db_name, name + '.json')

    @staticmethod
    def _is_legal_file(path):
        return os.path.exists(path) and os.path.getsize(path) > 0

    def _create_database(self):
        path = os.path.join(self._db_path, self._db_name)
        if not os.path.exists(path):
            os.mkdir(path)

    def _create_table(self, name, fields):
        data = None

        if self._is_legal_file(self._meta_path):
            with open(self._meta_path, 'r') as meta_file:
                data = json.load(meta_file)
            for table in data:
                if table['table_name'] == name:
                    raise Exception('Table already exists')

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
        meta = open(self._meta_path, 'r')
        data = json.load(meta)
        meta.close()

        for table in data:
            if table['table_name'] == name:
                return str('create table ' + name + ' (' + ', '.join(
                    [' '.join(list(i.values())) for i in table['columns']]) + ')')

    def _insert_into_table(self, name, fields):
        values = fields
        table_path = self._get_table_path(name)

        data_structure = None
        if self._is_legal_file(self._meta_path):
            meta = open(self._meta_path, 'r')
            meta_data = json.load(meta)
            meta.close()
            for table in meta_data:
                if table['table_name'] == name:
                    data_structure = table['columns']

        if data_structure is None:
            raise Exception('Table does not exists')

        table_data = None
        if self._is_legal_file(table_path):
            table = open(table_path, 'r')
            table_data = json.load(table) if table is not None else None
            table.close()

        new_data = {}
        for index, item in enumerate(data_structure):
            if list(item.values())[1] == 'number':
                values[index] = int(values[index])
            new_data.update({list(item.values())[0]: values[index]})

        with open(table_path, 'w') as table_file:
            if isinstance(table_data, list):
                table_data.append(new_data)
                json.dump(table_data, table_file, ensure_ascii=False)
            else:
                json.dump([new_data], table_file, ensure_ascii=False)

    def _select_from_table(self, name, columns, condition=None):
        if not self._is_legal_table(name):
            raise Exception('Table does not exists')

        if not self._is_legal_file(self._get_table_path(name)):
            return None

        result = []
        with open(self._get_table_path(name)) as table_file:
            data = json.load(table_file)
            if columns == '*':
                return data

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
        table_path = self._get_table_path(name)

        with open(table_path, 'r') as table_file:
            data = json.load(table_file)

        with open(table_path, 'w') as table_file:
            column = condition[0]
            operator = condition[1]
            value = condition[2]

            for item in data:
                if self._handle_condition(item[column], operator, value):
                    del item[column]

            json.dump(data, table_file, ensure_ascii=False)

    def _update_table(self, name, values, condition):
        table_path = os.path.join(self._db_path, self._db_name, name + '.json')

        with open(table_path, 'r') as table_file:
            data = json.load(table_file)

        with open(table_path, 'w') as table_file:
            column = condition[0]
            operator = condition[1]
            value = condition[2]

            for row in data:
                if self._handle_condition(row[column], operator, value):
                    for column in row:
                        if values[column]:
                            row[column] = type(row[column])(values[column])

            json.dump(data, table_file, ensure_ascii=False)

    def _handle_condition(self, value1, operator, value2):
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
