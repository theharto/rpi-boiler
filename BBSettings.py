import json
import threading

class BBSettings:
	def __init__(self):
		self.__settings = {}
		self.__lock = threading.Lock()
		
		self.set('client_refresh', 30)
		self.set('thermometer_refresh', 300)
		self.set('controller_tick', 20)
		self.set('hysteresis', 0.5)
		self.set('min_switching', 60)
		self.set('debug_mode', 1)
		self.set('test_mode', 1)
		self.set('relay_gpio', 20)
		self.set('led_gpio', 21)
		#self.set('meta_bools', ['debug_mode', 'test_mode'])
		#self.set('meta_restart', ['relay_gpio', 'led_gpio'])
		
	def __str__(self):
		return str(self.settings)
	   
	def get_json(self):
		"""
		json = '{ '
		for k, v in self.settings.items():
			
			t = type(v)
			if t == int:
				json += '"%s":%d ' % (k, v)
			elif t == float:
				json += '"%s":[%.2f, "float"], ' % (k, v)
			elif t == bool:
				json += '"%s":[%d, "bool"], ' % (k, v)
			elif t == str:
				json += '"%s":["%s", "str"], ' % (k, v)
		json += '"null", 0 }'
		json = str(self.settings)
		json = '{ "name":"John", "age":31, "city":"New York" }'
		"""
		with self.__lock:
			return json.dumps(self.__settings)
	
	def set(self, key, value):
		with self.__lock:
			if (key in self.__settings):
				# type is important, so cast to original type
				t = type(self.__settings[key])
				value = t(value)
			print("SETTINGS.set:", key, value)
			self.__settings[key] = value
		
	def get(self, key):
		with self.__lock:
			return self.__settings[key]
		
	def remove(self, key):
		with self.__lock:
			if key in self.__settings:
				self.__settings.pop(key, None)
