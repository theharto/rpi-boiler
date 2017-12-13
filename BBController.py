import threading
import time
import BBSharedData
import RPi.GPIO as GPIO
from termcolor import cprint, colored
from datetime import datetime, date
#import BBSettings
import BBLed


# Time of day in seconds
def tod(h, m=0, s=0):
	return (h*3600) + (m*60) + s
	
def tod_to_str(s):
	h = int(s / 3600)
	s -= h * 3600
	m = int(s / 60)
	s -= m * 60
	return str(h) + ":" + str(m) + ":" + str(s)
	
def str_to_tod(s):
	t = s.split(':')
	return tod(int(t[0]), int(t[1]), int(t[2]))

def tod_now():
	now = datetime.now()
	midnight = datetime(now.year, now.month, now.day)
	return (now - midnight).seconds
	
id_count = 0
class BBEvent:
	def __init__(self, start, end, temp):
		global id_count
		
		self.start_time = start if type(start) is int else str_to_tod(start)
		self.end_time = end if type(end) is int else str_to_tod(end)
		self.temp = temp
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
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.RELAY_ON = GPIO.LOW
		self.RELAY_OFF = GPIO.HIGH
		
		self.data = data
		self.wake_signal = threading.Condition()
		self.led = BBLed.BBLed(self.data.settings.get('led_gpio'))
		self.relay_pin = self.data.settings.get('relay_gpio')
		self.main_thread = threading.current_thread()
		
		self.thermometer_temp = 20.0
		self.override_event_queue = []
		self.event_queue = [BBEvent(tod(10, 12, 0), tod(12, 0, 0), 0), BBEvent(tod(0, 0, 0), tod(24, 0, 0), 25.0)]
		self.event_queue.append(BBEvent(tod(11), tod(17), 17))
		self.event_queue.insert(0, BBEvent(tod(13), tod(15), 25))
		self.event_queue.append(BBEvent(tod(9), tod(13,30), 50))
		self.add_event("1:45:30", "1:59:59", 30, override=True)
		self.add_event("5:0:0", "19:0:0", 18)
		
		print(self.event_queue)
		
		self.event_queue.sort()
		
		print(self.event_queue)
		
		
	def add_event(self, start, end, temp, override=False):
		e = BBEvent(start, end, temp)
		if override:
			self.override_event_queue.append(e)
			self.override_event_queue.sort()
		else:
			self.event_queue.append(e)
			self.event_queue.sort()
	
	def wake_controller_thread(self):
		with self.wake_signal:
			self.wake_signal.notify()

	def shutdown(self):
		self.running = False # assignments are atomic
		self.wake_controller_thread()
		
	def __set_boiler(self, on):
		test_mode = self.data.settings.get('test_mode')
		
		cprint("Set boiler=%d gpio=%d %s" % (on, self.relay_pin, ("[TEST]" if test_mode else "")), ("red" if on else "blue"))
		self.led.on(on)
		if not test_mode:
			GPIO.output(self.relay_pin, (self.RELAY_ON if on else self.RELAY_OFF))
	
	def run(self):
		cprint("Controller thread started", "red")
		self.previous_boiler_state = self.data.boiler_on
		self.previous_change_time = int(time.time())
		
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.data.settings.get('relay_gpio'), GPIO.OUT, initial=self.RELAY_OFF)
		
		self.running = True
		while self.running:
			current_time = int(time.time())
			print ("BBController.run() -- tick -- " + datetime.fromtimestamp(current_time).strftime('%H:%M:%S'))
			
			if not self.main_thread.is_alive():
				cprint("Main thread terminated! Shuting down...", "red")
				break
			
			self.led.flash()
			
			active_event = None
			now = tod_now()
			# check override events first
			self.override_event_queue.sort()
			for e in self.override_event_queue:
				if (e.start_time <= now) and (e.end_time > now):
					active_event = e
					cprint("Active override event", "magenta");
					break
			
			# if no override active, then normal events
			if active_event is None:
				self.event_queue.sort()
				cprint("Active normal event", "magenta")
				for e in self.event_queue:
					if (e.start_time <= now) and (e.end_time > now):
						active_event = e
						break
					
			cprint("Active event = " + str(active_event), "blue")
			self.__set_boiler(active_event.temp > self.thermometer_temp)
			
			# sleep for tick, but wake up if signalled
			with self.wake_signal:
				self.wake_signal.wait(self.data.settings.get('controller_tick'))
			
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
		# make sure that boiler is off
		self.__set_boiler(0)
		
		self.led.stop()
		self.led.join()
		
		GPIO.cleanup()
		cprint("Controller thread ended", "red")

if __name__ == "__main__":
	import BBMain
	BBMain.go()
