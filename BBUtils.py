import socket
import sys, os, random, hashlib

import logging
log = logging.getLogger(__name__)

def random_token(n):
	return ''.join(random.SystemRandom().choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~") for _ in range(n))

def session_hash(key, ip4):
	data = (key + ip4).encode()
	return hashlib.sha512(data).hexdigest()[:64]

#
#
#
class ErrorLogger():
	def __init__(self):
		self.__cache = ''
		
	def write(self, str):
		for line in str.splitlines():
			logging.error(line)
		'''
	def write(self, str):
		for line in str.splitlines():
			if line.endswith('\n'):
				if (self.__cache == ''):
					logging.error(line.rstrip())
				else:
					logging.error(self.__cache + line.rstrip())
					self.__cache = ''
			else:
				self.__cache += line
	
	def flush(self):
		if self.__cache != '':
			logging.error("!!! FLUSH !!!" + self.__cache)
			self.__cache = ''
			'''
	def flush(self):
		pass

#
# sudo_action(string)
# - send string to port 5511
#
def sudo_action(a):
	log.info("sudo_action %s", a)
	
	#os.system("echo '" + a + "' | nc -w 0 localhost 5511");
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		r = s.connect(('', 5511))
		s.sendall(a.encode())
		s.close()
	except:
		log.exception("sudo_action exception")