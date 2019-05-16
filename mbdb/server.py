import pickle
import socket

from mbdb.mbdb import mbdb


class mbdbServer:
	def __init__(self, name = 'srv', host = '127.0.0.1', port = 65432):
		self._name = name
		self._host = host
		self._port = port

		self._db = mbdb(name, type = 'server')

	def run(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((self._host, self._port))
			s.listen()
			while True:
				conn, addr = s.accept()
				with conn:
					data = pickle.loads(conn.recv(4096))
					if data[0] == 'begin_transaction':
						self._db.exec('begin_transaction', token = data[1])
						conn.sendall(pickle.dumps(True))
					elif data[0] == 'commit':
						self._db.exec('commit', token = data[1])
						conn.sendall(pickle.dumps(True))
					elif data[0] == 'killsrv':
						conn.sendall(pickle.dumps('server is down now'))
						return 0
					else:
						conn.sendall(pickle.dumps(self._db.exec(data[0], token = data[1])))
