import logging
log = logging.getLogger(__name__)

import json, threading
import collections # NB python3.6 uses ordered dictionary, so won't need this in future
import BBUtils

SETTINGS_FNAME = "settings.json"

class BBSettings:
	def __init__(self):
		self.__settings = collections.OrderedDict()
		self.__lock = threading.Lock()

		self.__set_defaults()
		self.__load_settings()
	
	def __set_defaults(self):
		with self.__lock:
			self.__settings['client_refresh'] = 30
			self.__settings['therm_refresh'] = 300
			self.__settings['controller_tick'] = 120
			self.__settings['hysteresis'] = 0.5
			self.__settings['min_switching'] = 60 #'rest' ?
			self.__settings['live_mode'] =  0
			self.__settings['relay_gpio'] = 15
			self.__settings['led_gpio'] = 21
			self.__settings['session_password'] = 'changeme'
			self.__settings['cookie_name'] = 'hf-' + BBUtils.random_token(12)
			self.__settings['cookie_ttl'] = 90 * 24 * 60 * 60
			self.__settings['bool_test'] = True

	def __save_settings(self):
		try:
			with self.__lock, open(SETTINGS_FNAME, 'w') as f:
				f.write(json.dumps(self.__settings, indent=4))
			log.info("Saved to %s", SETTINGS_FNAME)
		except IOError:
			log.exception("Error saving to %s", SETTINGS_FNAME)
	
	def __load_settings(self):
		try:
			with self.__lock, open(SETTINGS_FNAME, 'r') as f:
				self.__settings.update(json.load(f, object_pairs_hook=collections.OrderedDict))
			log.info("Loaded from %s", SETTINGS_FNAME)
		except IOError:
			log.warning("Unable to load %s", SETTINGS_FNAME)

	def get_json(self):
		with self.__lock:
			return json.dumps(self.__settings)

	def set(self, key, value):
		with self.__lock:
			if (key in self.__settings):
				# type is important, so cast to original type
				t = type(self.__settings[key])
				value = t(value)
			self.__settings[key] = value
		log.info("Set ['%s'] = %s", key, value)
		self.__save_settings()
	
	def get(self, key):
		with self.__lock:
			return self.__settings[key]
	
	def remove(self, key):
		with self.__lock:
			if key in self.__settings:
				self.__settings.pop(key, None)
		self.__save_settings()

	def reset_to_defaults(self):
		self.__set_defaults()
		self.__save_settings()
	
