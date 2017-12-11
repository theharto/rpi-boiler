import json

class BBSettings:
	def __init__(self):
		self.settings = {}
		
		self.set('client_refresh', 30)
		self.set('thermometer_refresh', 300)
		self.set('controller_tick', 5)
		self.set('hysteresis', 0.5)
		self.set('min_switching', 60)
		self.set('debug_mode', 1)
		self.set('test_mode', 1)
		self.set('relay_gpio', 21)
		self.set('led_gpio', 2)
		#self.set('meta_bools', "blah blah")
		
	def __str__(self):
		return str(self.settings)
	   
	def toJSON(self):
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
		return json.dumps(self.settings)
	
	def set(self, key, value):
		if (key in self.settings):
			# type is important, so cast to original type
			t = type(self.settings[key])
			value = t(value)
		print("SETTINGS.set:", key, value)
		self.settings[key] = value
		
	def get(self, key):
		return self.settings[key]
		
	def remove(self, key):
		if key in self.settings:
			self.settings.pop(key, None)

if __name__ == "__main__":
	s = BBSettings()
	print(s)
	print("")
	
	s.set('keyb', 100)
	s.set('keya', 200)
	print(s.toJSON())
	
	s.set('keya', '300')
	s.set('keyd', 10.10)
	s.set('keye', True)
	print(s.toJSON())