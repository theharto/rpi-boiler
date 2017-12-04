from threading import Lock, Condition
from pprint import pprint

class BBSettings:
	def __init__(self):
		self.client_refresh = 30
        self.thermometer_refresh = 300
        self.controller_tick = 60
        self.debug_mode = True
        self.test_mode = False
       
    def toJSON():
    	json = '{ "client_refresh": %d,'
    	json += ' "thermometer_refresh": %d,'
    	json += ' "controller_tick": %d,'
    	json += ' "debug_mode": %d,'
    	json += ' "test_mode": %d }'
    	return json

class BBSharedData:
    def __init__(self):
        print "BBStatus.init(", self, ")"
        
        self.mode = "switch"
        self.boiler_on = False
        self.countdown_off_time = 0
        self.shutdown = False
        self.countdown_end = 1
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
