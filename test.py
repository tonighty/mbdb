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

        self._db.exec('insert into products values (1, CocaCola, base64, good)')
        self._db.exec('insert into products values (2, Pepsi, base64, bad)')

        value = self._db.exec('select id from products')
        self.assertEqual(1, value[0]['id'])

        value = self._db.exec('select name from products')
        self.assertEqual('CocaCola', value[0]['name'])

        value = self._db.exec('select id from products where id == 2')
        self.assertEqual(2, value[0]['id'])

    def test_delete(self):
        self._db.exec('create table products (id number)')

        for i in range(10):
            self._db.exec('insert into products values (%d)' % i)

        self._db.exec('delete from products where id > 5')

        self.assertEqual(len(self._db.exec('select id from products')), 5)

    def test_update(self):
        self._db.exec('create table products (id number)')

        for i in range(10):
            self._db.exec('insert into products values (%d)' % i)

        self._db.exec('update products set id = 1 where id > 5')

        self.assertEqual(len(self._db.exec('select id from products where id == 1')), 5)

    def tearDown(self):
        shutil.rmtree(self._db.get_database_path())


if __name__ == '__main__':
    unittest.main()
