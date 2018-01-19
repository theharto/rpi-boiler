import logging
log = logging.getLogger(__name__)

import time, threading, sys, os
import BBLed, BBUtils

def wifi_strength(max_strength=70.0):
#	with open("/proc/net/wireless") as f:
	try:
		with open("wireless") as f:
			f.readline()
			f.readline()
			l = f.readline().split()
			if not l:
				return 0
			#return 0
			return int(100.0 * (float(l[2]) / max_strength))
	except IOError:
		log.warn("Unable to open 'wireless'")
	return 0
	
is_active = False

class BBMonitor(threading.Thread):
	
	def __init__(self, led):
		threading.Thread.__init__(self)
		self.__led = led
		self.RECON_ATTEMPTS = 5
		self.RECON_WAIT_TIME = 20
		
	def wait_reconnection(self):
		for i in range(0, self.RECON_ATTEMPTS):
			s = wifi_strength()
			log.info("%d. Wifi strength = %d%%", i, s)
			if s > 0:
				log.info("Monitor ending - Wifi back up")
				return True
			time.sleep(self.RECON_WAIT_TIME)
		return False
	
	def run(self):
		global is_active
		is_active = True
		log.info("BBMonitor started")
		self.__led.flashing(1)
		
		if not self.wait_reconnection():
			### if it gets to here then what next? restart networking? reboot machine?
			BBUtils.sudo_action("stop_net")
			time.sleep(30)
			BBUtils.sudo_action("start_net")
			time.sleep(20)
			s = wifi_strength()
			log.info("Wifi strength = %d%%", s)
			if not s > 0:
				log.warn("Unable to reconnect wifi, rebooting ... ")
				BBUtils.sudo_action("reboot")
		
		log.info("BBMonitor ended")
		self.__led.flashing(0)
		is_active = False
		