import json
import os
import sys
from mbdb.sqlparser import parse

sys.path.insert(0, "../..")

if sys.version_info[0] >= 3:
    raw_input = input

DEFAULT_DB_PATH = os.path.join(os.sep, 'mbdb')


class mbdb():

    def __init__(self, name):

        self._db_name = name
        self._create_database()

    def exec(self, statement):
        sql = parse(statement)
        print('TEST ' + str(sql))

        if sql is None:
            return

        if sql[0] == 'create':
            return self._create_table(sql[2], sql[3])

        elif sql[0] == 'show':
            return self._show_create_table(sql[3])

        elif sql[0] == 'insert':
            return self._insert_into_table(sql[2], sql[5])

        elif sql[0] == 'select':
            return self._select_from_table(sql[3], sql[1])

    def _check_for_db(self):
        if not self._db_name:
            raise Exception('First open or create database')

    def _create_database(self):
        path = os.path.join(DEFAULT_DB_PATH, self._db_name)
        if not os.path.exists(path):
            os.mkdir(path)

    def _create_table(self, name, fields):
        if not self._db_name:
            print('First open or create database')
        else:
            path_meta = os.path.join(DEFAULT_DB_PATH, self._db_name, '_META.json')
            data = None
            if os.path.exists(path_meta):
                try:
                    data = json.load(open(path_meta, 'r'))
                    for table in data:
                        if table['table_name'] == name:
                            print('Table already exists')
                            return 1
                except json.JSONDecodeError:
                    print('Database is empty')
            new_data = {
                'table_name': name,
                'columns': fields,
            }
            with open(path_meta, 'w') as metafile:
                if isinstance(data, list):
                    data.append(new_data)
                    json.dump(data, metafile)
                else:
                    json.dump([new_data], metafile)

            path_table = os.path.join(DEFAULT_DB_PATH, self._db_name, name + '.json')
            open(path_table, 'w')

    def _show_create_table(self, name):
        if not self._db_name:
            print('First open or create database')
        else:
            path_meta = os.path.join(DEFAULT_DB_PATH, self._db_name, '_META.json')
            data = json.load(open(path_meta, 'r'))
            for table in data:
                if table['table_name'] == name:
                    print('create table ' + name + ' (' + ', '.join(
                        [' '.join(list(i.values())) for i in table['columns']]) + ')')

    def _insert_into_table(self, name, fields):
        if not self._db_name:
            print('First open or create database')
        else:
            path_meta = os.path.join(DEFAULT_DB_PATH, self._db_name, '_META.json')
            values = fields
            path_table = os.path.join(DEFAULT_DB_PATH, self._db_name, name + '.json')
            data_scructure = None
            if os.path.exists(path_meta):
                try:
                    meta_data = json.load(open(path_meta, 'r'))
                    for table in meta_data:
                        if table['table_name'] == name:
                            data_scructure = table['columns']
                except json.JSONDecodeError:
                    print('Create table first ffs')
                    return 1
            if data_scructure == None:
                print('Create table first ffs')
                return 1
            table_data = None
            if os.path.exists(path_table):
                try:
                    table_data = json.load(open(path_table, 'r'))
                except json.JSONDecodeError:
                    print('Creating table file...')
            new_data = {}
            for index, item in enumerate(data_scructure):
                if list(item.values())[1] == 'number':
                    values[index] = int(values[index])
                new_data.update({list(item.values())[0]: values[index]})
            with open(path_table, 'w') as table_file:
                if isinstance(table_data, list):
                    table_data.append(new_data)
                    json.dump(table_data, table_file, ensure_ascii=False)
                else:
                    print(new_data)
                    json.dump([new_data], table_file, ensure_ascii=False)

    def _select_from_table(self, name, columns):
        table_path = os.path.join(DEFAULT_DB_PATH, self._db_name, name + '.json')
        result = []
        with open(table_path) as table_file:
            data = json.load(table_file)
            if columns == '*':
                return data

            for row in data:
                row_res = {}
                for column in columns:
                    val = row.get(column)
                    if val:
                        row_res[column] = val
                if row_res != {}:
                    result.append(row_res)

        return result
