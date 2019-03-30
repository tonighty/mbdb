[![Build Status](https://travis-ci.com/tonighty/mbdb.svg?branch=develop)](https://travis-ci.com/tonighty/mbdb)

# mbdb

Simple Database Management System.

## Installation

```sh
$ python setup.py install
```

## Usage

```python
from mbdb.mbdb import mbdb

db = mbdb('table-name', 'table-path')
db.exec('create table users (id number, name string)')
db.exec('insert into users values (1, John)')
db.exec('select * from users')
```

## Testing

```sh
$ python -m unittest discover
$ tox
```