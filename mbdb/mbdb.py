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

        if sql == None:
            raise Exception('Error')

        if sql[0] == 'create':
            self._create_table(sql[2], sql[3])

        elif sql[0] == 'show':
            self._show_create_table(sql[3])

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
