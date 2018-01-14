import logging
log = logging.getLogger(__name__)

import time, threading
import BBLed, BBUtils

def wifi_strength(max_strength=70.0):
	with open("/proc/net/wireless") as f:
		f.readline()
		f.readline()
		l = f.readline().split()
		if not l:
			return 0
		#return 0
		return int(100.0 * (float(l[2]) / max_strength))

class LedFlasher:
	def __init__(self, led):
		self.__led = led
		
	def __enter__(self):
		log.info("enter")
		self.__led.flashing(1)

	def __exit__(self, type, value, traceback):
		log.info("exit")
		self.__led.flashing(0)

class BBMonitor(threading.Thread):
	
	def __init__(self, led):
		threading.Thread.__init__(self)
		self.__led = led
		self.RECON_ATTEMPTS = 1
		self.RECON_WAIT_TIME = 1
		
		log.info("BBMonitor(%s)", str(led))
	
	def run(self):
		log.info("BBMonitor started")
		
		s = 0
		with LedFlasher(self.__led):
			for i in range(0, self.RECON_ATTEMPTS):
				s = wifi_strength()
				log.info("%d. Wifi strength = %d", i, s)
				if s > 100:
					log.info("Monitor ending - Wifi back up")
					return
				time.sleep(self.RECON_WAIT_TIME)
			
			### if it gets to here then what next? restart networking? reboot machine
			BBUtils.sudo_action("stop_net")
			time.sleep(1)
			BBUtils.sudo_action("start_net")
			time.sleep(1)
			#BBUtils.sudo_action("reboot")
			s = wifi_strength()
			log.info("Wifi strength = %d", s)
		
		log.info("BBMonitor ended")
		
if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	log.info("BBMonitor test")
	
	if (wifi_strength() >= 0):
		led = BBLed.BBLed(21)
		led.start()
		log.info("flash")
		led.flash()
		log.info("sleep 2")
		time.sleep(2)	
		m = BBMonitor(led)
		m.start()
		m.join()
		led.stop()
		led.join()
	log.info("End of test")