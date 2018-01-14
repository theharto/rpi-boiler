import logging
log = logging.getLogger(__name__)

import socket
import sys, os


#
# sudo_action(string)
# - send string to port 5511
#
def sudo_action(mess):
	log.info("sudo_action %s", mess)
	
	#os.system("echo '" + mess + "' | nc -w 0 localhost 5511");
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		r = s.connect(('', 5511))
		s.sendall(mess.encode())
		s.close()
	except:
		log.exception("sudo_action exception")