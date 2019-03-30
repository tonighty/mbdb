import shutil

from mbdb.mbdb import mbdb
import unittest


class TestDB(unittest.TestCase):

    def setUp(self):
        self._db = mbdb('test-table')

    def test_show_create_table(self):
        query = 'create table users (id number, name string)'
        self._db.exec(query)
        self.assertEqual(self._db.exec('show create table users'), query)

        query = 'create table products (id number, name string, photo string, description string)'
        self._db.exec(query)
        self.assertEqual(self._db.exec('show create table products'), query)

    def test_insert_select(self):
        query = 'create table products (id number, name string, photo string, description string)'
        self._db.exec(query)

        self._db.exec('insert into products values (1, CocaCola, base64, norm)')

        value = self._db.exec('select id from products')
        self.assertEqual(1, value[0]['id'])

        value = self._db.exec('select name from products')
        self.assertEqual('CocaCola', value[0]['name'])

    def tearDown(self):
        shutil.rmtree(self._db.get_database_path())


if __name__ == '__main__':
    unittest.main()
