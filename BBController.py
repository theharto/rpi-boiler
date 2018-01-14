import logging
log = logging.getLogger(__name__)

import time, threading, json
import RPi.GPIO as GPIO
from termcolor import cprint
from datetime import datetime

import BBSettings, BBLed, BBMonitor

# Time of day in seconds
def tod(h, m=0, s=0):
	return int((h*3600) + (m*60) + s)

def tod_to_str(s):
	h = int(s / 3600)
	s -= h * 3600
	m = int(s / 60)
	s -= m * 60
	return "%d:%d:%d" % (h, m, s)

def str_to_tod(s):
	t = s.split(':')
	return tod(int(t[0]), int(t[1]), int(t[2]))

def tod_now():
	now = datetime.now()
	midnight = datetime(now.year, now.month, now.day)
	now = now - midnight
	info.info("tod_now %s => %d", str(now), tod(now.hours, now.minutes, now.seconds))
	return tod(now.hours, now.minutes, now.seconds)

id_count = 0
class BBEvent:
	def __init__(self, start, end, temp):
		global id_count
		
		if type(start) is str:
			start = str_to_tod(start)
		if type(end) is str:
			end = str_to_tod(end)
		
		self.start_time = int(start)
		self.end_time = int(end)
		self.temp = float(temp)
		self.id = id_count
		id_count += 1
		
		log.info("new " + str(self))
	
	def is_active(self, t):
		return (self.start_time <= t) and (self.end_time > t)
	
	# sort by id descending
	def __lt__(self, other):
		return (self.id > other.id)
	
	def __str__(self):
		return "(BBEvent%d %s, %s, %d)" % (self.id, tod_to_str(self.start_time), tod_to_str(self.end_time), self.temp)
		
	def __repr__(self):
		return self.__str__()
	
	def to_json(self):
		return ""

#
#
#
class BBController(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.RELAY_ON = GPIO.LOW
		self.RELAY_OFF = GPIO.HIGH
		
		self.settings = BBSettings.BBSettings()
		self.__led = BBLed.BBLed(self.settings.get('led_gpio'))
		self.__relay_pin = self.settings.get('relay_gpio')
		
		self.__wake_signal = threading.Condition()
		self.__main_thread = threading.current_thread()
		self.__running = False
		self.__boiler_on = False
		self.__therm_temp = 50
		self.__override_event = None
		self.__event_queue = []
		
		self.add_event("0:0:0", "24:0:0", 0)

	def __enter__(self):
		self.__wake_signal.acquire()
		log.info("Controller locked")

	def __exit__(self, type, value, traceback):
		self.__wake_signal.notifyAll()
		self.__wake_signal.release()
		log.info("Controller unlocked")

	#
	# add_event()
	#
	def add_event(self, start, end, temp):
		with self:
			self.__event_queue.insert(0, BBEvent(start, end, temp))
	
	#
	# set_override_event()
	#
	def set_override_event(self, start, end, temp):
		with self:
			self.__override_event = BBEvent(start, end, temp)

	#
	# remove_override_event()
	#
	def remove_override_event(self):
		with self:
			self.__override_event = None

	#
	# del_event()
	#
	def del_event(self, e_id):
		with self:
			if e_id == self.__override_event.id:
				self.__override_event = None
				return
			for e in self.__event_queue[:]: #note: makes copy of list to search
				if e_id == e.id:
					self.__event_queue.remove(e)
					return

	#
	# get_status_json()
	#
	def get_status_json(self):
		with self.__wake_signal:
			status = {}
			status['server_time'] = int(time.time())
			status['boiler_on'] = self.__boiler_on
			status['therm_temp'] = self.__therm_temp
			
			if self.__override_event:
				status['override_event'] = self.__override_event.__dict__
			
			status['event_queue'] = []
			self.__event_queue.sort()
			for e in self.__event_queue:
				status['event_queue'].append(e.__dict__)
				
		return json.dumps(status)
	
	#
	# set_therm_temp(temp)
	#
	def set_therm_temp(self, t):
		with self:
			self.__therm_temp = float(t)
	
	#
	# shutdown()
	#
	def shutdown(self):
		with self:
			self.__running = False
	
	#
	# __get_active_event()
	#
	def __get_active_event(self):
		now = int(time.time())
		tod_now = tod_now()
		
		with self.__wake_signal:
			if self.__override_event:
				if self.__override_event.is_active(now):
					return self.__override_event
				if self.__override_event.end_time < now:
					log.info("Override event expired, deleting %s", str(self.__override_event))
					self.__override_event = None
			
			self.__event_queue.sort()
			for e in self.__event_queue:
				if e.is_active(tod_now):
					return e
		return None
	
	#
	# __evaluate_status()
	#
	def __evaluate_status(self):
		with self.__wake_signal:
			log.info("eval")
			active_event = self.__get_active_event()
			log.info("Active event = %s" + str(active_event))
			
			if active_event:
				# Adjust target temperature for hystersis
				if self.__boiler_on:
					adj_target_temp = active_event.temp + self.settings.get('hysteresis')
				else:
					adj_target_temp = active_event.temp - self.settings.get('hysteresis')
				
				cprint("boiler_on  = %d" % (self.__boiler_on), "cyan")
				cprint("event_temp = %f" % (active_event.temp), "cyan")
				cprint("adj_t_temp = %f" % (adj_target_temp), "cyan")
				cprint("therm_temp = %f" % (self.__thermometer_temp), "cyan")
				
				self.__boiler_on = self.__therm_temp < adj_target_temp
			else:
				self.__boiler_on = False
	
	#
	# run()
	# TODO - guard against frequent toggling
	#
	def run(self):
		log.info("Controller thread started")
		
		# set up gpios
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__relay_pin, GPIO.OUT, initial=self.RELAY_OFF)
		self.__led.start()
		
		# controller thread loop
		self.__boiler_on = False
		self.__running = True
		while True:
			log.info("Tick")
						
			# pulse led on tick
			self.__led.flash()
			
			# Check main thread still alive
			if not self.__main_thread.is_alive():
				log.info("Main thread terminated. Shutting down...")
				break
			
			# Check if network is connected
			s = BBMonitor.wifi_strength()
			if s == 0:
				log.warn("Wifi signal lost, launching monitor")
				BBMonitor.BBMonitor(self.__led).start()
			log.info("Wifi strength = %d", s)
			
			# do stuff inside lock, so that vars cannot be changed while awake
			with self.__wake_signal:
				
				# break while loop if not running
				if not self.__running:
					break
				
				self.__evaluate_status()
				
				# Turn on/off led and relay
				self.__led.on(self.__boiler_on)
				if self.settings.get('live_mode'):
					GPIO.output(self.__relay_pin, (self.RELAY_ON if self.__boiler_on else self.RELAY_OFF))
				
				# sleep for tick, but wake up if signalled
				self.__wake_signal.wait(self.settings.get('controller_tick'))
				
			"""
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
				
				self.__set_boiler(boiler_on)
			"""
		
		# Shutdown ...
		# make sure that boiler is off
		self.__set_boiler(0)
		
		self.__led.stop()
		self.__led.join()
		
		GPIO.cleanup()
		log.info("Controller thread ended")
