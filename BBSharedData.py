from threading import Lock, Condition
from pprint import pprint

class BBSettings:
	def __init__(self):
		self.client_refresh = 30
		self.thermometer_refresh = 300
		self.controller_tick = 5
		self.hysteresis = 0.5
		self.min_switching = 60
		self.debug_mode = True
		self.test_mode = False
		self.gpio = 21
	
	def __str__(self):
		return str(vars(self))
	   
	def toJSON(self):
		json = '{ "client_refresh": %d,' % (self.client_refresh)
		json += ' "thermometer_refresh": %d,' % (self.thermometer_refresh)
		json += ' "controller_tick": %d,' % (self.controller_tick)
		json += ' "hysteresis": %.2f,' % (self.hysteresis)
		json += ' "min_switching": %d,' % (self.min_switching)
		json += ' "debug_mode": %d,' % (self.debug_mode)
		json += ' "test_mode": %d, ' % (self.test_mode)
		json += ' "gpio": %d }' % (self.gpio)
		return json

class BBSharedData:
	def __init__(self):
		self.boiler_on = False
		self.shutdown = False
		self.pending = True
		
		self.mode = "switch"
		self.countdown_off_time = 0
		self.target_temp = 18.0
		self.thermometer_temp = 99.0
		self.thermometer_update_time = 0
		
		self.settings = BBSettings()
		
		self.schedule = []
		self.lock = Lock()

	def __enter__(self):
		self.lock.acquire()
		
	def __exit__(self, type, value, traceback):
		self.lock.release()

bbp_id = 0
class BBPeriod:
	def __init__(self, start, stop, temperature=20, recurring=False):
		global bbp_id
		bbp_id += 1
		self.id = bbp_id
		self.start = start
		self.stop = stop
		self.temperature = 20
		self.recurring = recurring

	def __repr__(self):
		return "<BBPeriod id=%d start=%d, stop=%d, temperature=%d, recurring=%d>" % (self.id, self.start, self.stop, self.temperature, self.recurring)
