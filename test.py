from mbdb.mbdb import mbdb

db = mbdb('mega')

db.exec('create table users (id number, name string)')
db.exec('insert into users values (1, John)')
db.exec('insert into users values (2, Dick)')
db.exec('insert into users values (3, Richard)')
rows = db.exec('select * from users')
print(rows)
