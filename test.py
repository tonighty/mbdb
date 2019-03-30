import shutil

from mbdb.mbdb import mbdb
import unittest


class TestDB(unittest.TestCase):

    def test_show_create_table(self):
        db = mbdb('test-case')

        query = 'create table users (id number, name string)'
        db.exec(query)
        self.assertEqual(db.exec('show create table users'), query)

        query = 'create table products (id number, name string, photo string, description string)'
        db.exec(query)
        self.assertEqual(db.exec('show create table products'), query)

    def tearDown(self):
        shutil.rmtree('mbdb-test-db')


if __name__ == '__main__':
    unittest.main()
