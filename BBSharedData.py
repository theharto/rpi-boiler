from threading import Lock, Condition
import BBSettings

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
		
		self.settings = BBSettings.BBSettings()
		
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
