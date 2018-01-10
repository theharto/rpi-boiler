import json
import threading
import collections # NB python3.6 uses ordered dictionary, so won't need this in future

class BBSettings:
	def __init__(self):
		self.__settings = collections.OrderedDict()
		self.__lock = threading.Lock()
		
		# Set default values
		self.__settings['client_refresh'] = 30
		self.__settings['thermometer_refresh'] = 300
		self.__settings['controller_tick'] = 60
		self.__settings['hysteresis'] = 0.5
		self.__settings['min_switching'] = 60 #'rest' ?
		self.__settings['debug_mode'] = 1
		self.__settings['test_mode'] =  1
		self.__settings['relay_gpio'] = 15
		self.__settings['led_gpio'] = 21
		#self.__settings['meta_bools'] = ['debug_mode', 'test_mode']
		#self.__settings['meta_restart'] = ['relay_gpio', 'led_gpio']
		
		# Read json from settings file, if it exists
		try:
			with open('settings.json', 'r') as f:
				data = json.load(f)
				print("loaded json")
				print(data)
		except IOError:
			print("settings.json file not found, using default values")
			
	def __str__(self):
		with self.__lock:
			return str(self.settings)
	
	def get_json(self):
		with self.__lock:
			return json.dumps(self.__settings)
	
	def set(self, key, value):
		with self.__lock:
			if (key in self.__settings):
				# type is important, so cast to original type
				t = type(self.__settings[key])
				value = t(value)
			print("settings.set:", key, value)
			self.__settings[key] = value
			
			# save to settings file
			with open('settings.json', 'w') as f:
				f.write(json.dumps(self.__settings))
		
	def get(self, key):
		with self.__lock:
			return self.__settings[key]
		
	def remove(self, key):
		with self.__lock:
			if key in self.__settings:
				self.__settings.pop(key, None)
				

if __name__ == "__main__":
	s = BBSettings()
	print(s.get_json())
