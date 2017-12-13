import time, threading
import RPi.GPIO as GPIO
from termcolor import cprint
from datetime import datetime, date

import BBSettings, BBLed

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
	return int((now - midnight).seconds)

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
		
		cprint("new event %d %d %d %d" % (self.id, self.start_time, self.end_time, self.temp), "green")
	
	# sort by id descending
	def __lt__(self, other):
		return (self.id > other.id)
	
	def __str__(self):
		return "(BBEvent%d %s, %s, %d)" % (self.id, tod_to_str(self.start_time), tod_to_str(self.end_time), self.temp)
		
	def __repr__(self):
		return self.__str__()

class BBController(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.RELAY_ON = GPIO.LOW
		self.RELAY_OFF = GPIO.HIGH
		
		self.settings = BBSettings.BBSettings()
		self.__wake_signal = threading.Condition()
		self.__running = False
		self.__led = BBLed.BBLed(self.settings.get('led_gpio'))
		self.__relay_pin = self.settings.get('relay_gpio')
		self.__main_thread = threading.current_thread()
		self.__boiler_on = False
		self.__thermometer_temp = 17.9
		self.__override_event = None
		self.__event_queue = []
		
		self.add_event("0:0:0", "18:0:0", 18.5)
		self.add_event("1:45:30", "1:59:59", 30)
		self.set_override_event("5:0:0", "19:0:0", 18)

	def __enter__(self):
		self.__wake_signal.acquire()
		print("got controller lock")

	def __exit__(self, type, value, traceback):
		self.__wake_signal.notifyAll()
		self.__wake_signal.release()
		print("released controller lock")

	def add_event(self, start, end, temp):
		with self:
			self.__event_queue.insert(0, BBEvent(start, end, temp))
	
	def set_override_event(self, start, end, temp):
		with self:
			self.__override_event = BBEvent(start, end, temp)

	def del_event(self, e_id):
		# lock and check override & queue
		with self:
			if e_id == self.__override_event.id:
				self.__override_event = None
				return
			for e in self.__event_queue[:]: #note: makes copy to search
				if e_id == e.id:
					self.__event_queue.remove(e)
					return
				
	def get_status_json(self):
		r = '{"server_time":%d,"boiler_on":%d,"thermometer_temp":%.2f}' % (tod_now(), self.__boiler_on, self.__thermometer_temp) 
		return r

	def shutdown(self):
		with self:
			self.__running = False
			
	def set_thermometer_temp(self, t):
		with self:
			self.__thermometer_temp = float(t)

	def __set_boiler(self, on):
		test_mode = self.settings.get('test_mode')
		
		cprint("Set boiler=%d gpio=%d %s" % (on, self.__relay_pin, ("[TEST]" if test_mode else "")), ("red" if on else "blue"))
		self.__led.on(on)
		if not test_mode:
			GPIO.output(self.__relay_pin, (self.RELAY_ON if on else self.RELAY_OFF))

	def __get_active_event(self):
		now = tod_now()
		
		with self.__wake_signal:
			if self.__override_event:
				e = self.__override_event
				if (e.start_time <= now) and (e.end_time > now):
					return e
			
			self.__event_queue.sort()
			for e in self.__event_queue:
				if (e.start_time <= now) and (e.end_time > now):
					return e
		return None
	
	def run(self):
		cprint("Controller thread started", "red")
		self.previous_boiler_state = self.__boiler_on
		self.previous_change_time = int(time.time())
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__relay_pin, GPIO.OUT, initial=self.RELAY_OFF)
		self.__led.start()
		
		self.__boiler_on = False
		self.__running = True
		while True:
			current_time = int(time.time())
			print ("BBController.run() -- tick -- " + datetime.fromtimestamp(current_time).strftime('%H:%M:%S'))
			
			# Check main thread still alive
			if not self.__main_thread.is_alive():
				cprint("Main thread terminated! Shuting down...", "red")
				break
			
			self.__led.flash()
			
			# do stuff inside lock, so that vars cannot be changed while awake
			with self.__wake_signal:
				active_event = self.__get_active_event()
				cprint("Active event = " + str(active_event), "blue")
				
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
				
					self.__boiler_on = self.__thermometer_temp < adj_target_temp
				else:
					self.__boiler_on = False
		
				self.__set_boiler(self.__boiler_on)
				
				# sleep for tick, but wake up if signalled
				if self.__running:
					self.__wake_signal.wait(self.settings.get('controller_tick'))
				else:
					break
			
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
		# make sure that boiler is off
		self.__set_boiler(0)
		
		#cprint("closingn led thread", "red")
		self.__led.stop()
		self.__led.join()
		
		GPIO.cleanup()
		cprint("Controller thread ended", "red")
