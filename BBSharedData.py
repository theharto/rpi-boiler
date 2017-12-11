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
