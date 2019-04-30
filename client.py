from mbdb import mbdb

db = mbdb('srv', type = 'client')
db.exec('create table users (id number)')
db.exec('insert into users values (123)')
print(db.exec('select * from users'))
