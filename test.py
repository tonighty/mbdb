from mbdb.mbdb import mbdb

db = mbdb('mega')

db.exec('create table ua (hz string)')
db.exec('insert into ua values (mda)')
