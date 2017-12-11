import threading
import time
import BBSharedData
import RPi.GPIO as GPIO
from termcolor import cprint, colored
from datetime import datetime, date
#import BBSettings

def main_thread_running():
	for t in threading.enumerate():
		if t.name == "MainThread" and t.is_alive() == False:
			return False
	return True

# Time of day in seconds
def tod(h, m=0, s=0):
	return (h*3600) + (m*60) + s
	
def tod_str(s):
	h = int(s / 3600)
	s -= h * 3600
	m = int(s / 60)
	s -= m * 60
	return str(h) + ":" + str(m) + ":" + str(s)
	
def tod_now():
	now = datetime.now()
	midnight = datetime(now.year, now.month, now.day)
	return (now - midnight).seconds
	
id_count = 0
class BBEvent:
	def __init__(self, start, end, temp):
		global id_count
		self.start_time = start
		self.end_time = end
		self.temp = temp
		self.id = id_count
		id_count += 1
	
	def __str__(self):
		return "(BBEvent%d %s, %s, %d)" % (self.id, tod_str(self.start_time), tod_str(self.end_time), self.temp)
		
	def __repr__(self):
		return self.__str__()

class BBController(threading.Thread):
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.RELAY_ON = GPIO.LOW
		self.RELAY_OFF = GPIO.HIGH
		self.LED_ON = GPIO.HIGH
		self.LED_OFF = GPIO.LOW
		
		self.data = data
		self.wake_signal = threading.Condition()
		self.running = True
		
		# setup gpio pins
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.data.settings.get('relay_gpio'), GPIO.OUT, initial=self.RELAY_OFF)
		
		self.thermometer_temp = 20.0
		self.event_queue = [BBEvent(tod(10, 0, 0), tod(16, 0, 0), 0), BBEvent(tod(0, 0, 0), tod(24, 0, 0), 25.0)]
		self.event_queue.append(BBEvent(tod(11), tod(17), 17))
		
		print(self.event_queue)
		
		self.event_queue.sort(key=lambda e: e.start_time)
		
		print(self.event_queue)
		
		self.overide_event_queue = []
	
	def wake_controller_thread(self):
		with self.wake_signal:
			self.wake_signal.notify()

	# on change mode, try to maintain on/off status
	def set_mode(self, mode):
		if self.data.mode == mode:
			return;
		
		with self.data:
			if mode == "switch":
				self.data.mode = "switch"
			
			elif mode == "count":
				self.data.mode = "count"
				t = int(time.time())
				if self.data.boiler_on:
					if self.data.countdown_off_time < t:
						self.data.countdown_off_time = t + (60 * 60)
				else:
					self.data.countdown_off_time = t
					
			elif mode == "therm":
				self.data.mode = "therm"
		self.wake_controller_thread()

	def switch(self, active):
		with self.data:
			self.data.mode = "switch"
			self.data.boiler_on = (active == True)
			self.data.pending = True
		self.wake_controller_thread()
		
	def count(self, off_time):
		with self.data:
			self.data.mode = "count"
			t = int(time.time())
			# set limits - now, now + 4h
			self.data.countdown_off_time = max(t, min(t+(60 * 60 * 4), int(off_time)))
			self.data.boiler_on = (self.data.countdown_off_time > t)
			self.data.pending = True
		self.wake_controller_thread()
	
	#CHANGE NAME
	def therm(self, temp):
		temp = min(temp, 25.0)
		temp = max(temp, 5.0)
		with self.data:
			self.data.mode = "therm"
			self.data.target_temp = temp
		self.wake_controller_thread()
		
	def thermometer(self, temp):
		self.data.thermometer_temp = temp
		self.data.thermometer_update_time = time.time()
		self.wake_controller_thread()






	def shutdown(self):
		self.running = False # assignments are atomic
		self.wake_controller_thread()
		
	def __set_boiler(self, on):
		relay_pin = self.data.settings.get('relay_gpio')
		test_mode = self.data.settings.get('test_mode')
		
		cprint("Set boiler=%d gpio=%d %s" % (on, relay_pin, ("[TEST]" if test_mode else "")), ("red" if on else "blue"))
		if not test_mode:
			GPIO.output(relay_pin, (self.RELAY_ON if on else self.RELAY_OFF))
	
	def run(self):
		cprint("Controller thread started", "red")
		self.previous_boiler_state = self.data.boiler_on
		self.previous_change_time = int(time.time())
		
		while self.running:
			current_time = int(time.time())
			print ("BBController.run() -- tick -- " + datetime.fromtimestamp(current_time).strftime('%H:%M:%S'))
			
			if not main_thread_running():
				cprint("Main thread terminated, shuting down", "red")
				break;
			
			# check override events first
			
			self.event_queue.sort(key=lambda e: e.start_time)
			#for e in self.event_queue:
			
			
			
			"""
			with self.data:
				if self.data.mode == "switch":
					print ("mode = switch")
					
				elif self.data.mode == "count":
					print ( "mode = count")
					print ("countdown_off_time = ", self.data.countdown_off_time)
					print ("current_time = ", current_time)
					self.data.boiler_on = (self.data.countdown_off_time > current_time)
				
				elif self.data.mode == "therm":
					print ("mode = therm")
					print ("target_temp = ", self.data.target_temp)
					print ("thermometer_temp = ", self.data.thermometer_temp)
					self.data.boiler_on = (self.data.target_temp > self.data.thermometer_temp)
					self.data.boiler_on = False
					
				else:
					print ("mode = unknown")
					self.data.boiler_on = False
				
				boiler_on = self.data.boiler_on
				self.data.pending = False
				
				# test for state change, only change boiler if dt < min switching
				if self.data.boiler_on != self.previous_boiler_state:
					if (current_time - self.previous_change_time) < self.data.settings.settings['min_switching']:
						# state change unsuccessful, set pending
						cprint("Time since last change = " + str(current_time - self.previous_change_time), "blue")
						cprint("Boiler state change pending to ... " + str(self.data.boiler_on), "blue")
						boiler_on = self.previous_boiler_state
						self.data.pending = True
					else:
						# state change successful
						print (colored("Changing boiler state", "blue"))
						self.previous_boiler_state = self.data.boiler_on
						self.previous_change_time = current_time
				
				self.__set_boiler(boiler_on)"""
			
			# sleep for tick, but wake up if signalled
			with self.wake_signal:
				self.wake_signal.wait(self.data.settings.get('controller_tick'))

		# make sure that boiler is off
		self.__set_boiler(0)
		GPIO.cleanup()
		cprint("Controller thread ended", "red")

if __name__ == "__main__":
	import BBMain
	BBMain.go()
