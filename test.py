import shutil
import webbrowser

from mbdb.mbdb import mbdb
import unittest


class TestDB(unittest.TestCase):

	def setUp(self):
		self._db = mbdb('test-db')

	def test_parser(self):
		with self.assertRaises(SyntaxError):
			self._db.exec('create create table users (id number)')

		with self.assertRaises(SyntaxError):
			self._db.exec('create table users (id numbers, name strings)')

		with self.assertRaises(SyntaxError):
			self._db.exec('create show table users (id number, name string)')

		with self.assertRaises(SyntaxError):
			self._db.exec('create show users')

	def test_show_create_table(self):
		query = 'create table users (id number, name string)'
		self._db.exec(query)
		self.assertEqual(self._db.exec('show create table users'), query)

		with self.assertRaisesRegex(Exception, 'Table already exists'):
			self._db.exec(query)

		with self.assertRaises(SyntaxError):
			self._db.exec('create table jobs (id number[], name string)')

		query = 'create table products (id number, name string, photo string, description string)'
		self._db.exec(query)
		self.assertEqual(self._db.exec('show create table products'), query)

	def test_insert_select(self):
		query = 'create table products (id number, name string, photo string, description string)'
		self._db.exec(query)

		self._db.exec('insert into products values (1, "CocaCola", "https://cs7.pikabu.ru/post_img/big/2019/04/21/8/155585197917460600.jpg", "good")')
		self._db.exec('insert into products values (2, "Pepsi", "base64", "bad")')

		value = self._db.exec('select * from products')
		self.assertEqual(1, value[0]['id'])

		webbrowser.open(value[0]['photo'])

		value = self._db.exec('select name from products')
		self.assertEqual('CocaCola', value[0]['name'])

		value = self._db.exec('select id from products where id == 2')
		self.assertEqual(2, value[0]['id'])

		with self.assertRaisesRegex(Exception, 'Column "%s" does not exists in "%s"' % ('column', 'products')):
			self._db.exec('select column from products')

	def test_table_exception(self):
		with self.assertRaisesRegex(Exception, 'Table does not exists'):
			self._db.exec('show create table products')

		with self.assertRaisesRegex(Exception, 'Table does not exists'):
			self._db.exec('insert into products values (1, "CocaCola", "base64", "good")')

		with self.assertRaisesRegex(Exception, 'Table does not exists'):
			self._db.exec('select * from products')

		with self.assertRaisesRegex(Exception, 'Table does not exists'):
			self._db.exec('delete from products where id > 5')

		with self.assertRaisesRegex(Exception, 'Table does not exists'):
			self._db.exec('update products set id = 1 where id > 5')

	def test_condition_exception(self):
		query = 'create table products (id number, name string, photo string, description string)'
		self._db.exec(query)

		self._db.exec('insert into products values (1, "CocaCola", "https://cs7.pikabu.ru/post_img/big/2019/04/21/8/155585197917460600.jpg", "good")')
		self._db.exec('insert into products values (2, "Pepsi", "base64", "bad")')

		with self.assertRaisesRegex(Exception, 'Column "%s" does not exists in "%s"' % ('external_id', 'products')):
			self._db.exec('update products set id = 1 where external_id > 5')

		with self.assertRaisesRegex(ValueError, '"%s" must be type of "%s"' % ('five', type(1))):
			self._db.exec('update products set id = 1 where id > "five"')

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
