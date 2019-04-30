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
					data = conn.recv(4096).decode()
					res = pickle.dumps(self._db.exec(data))

					if isinstance(res, Exception):
						raise res
					else:
						return res
