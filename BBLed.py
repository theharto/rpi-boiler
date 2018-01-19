import RPi.GPIO as GPIO
import time, threading

class BBLed(threading.Thread):
	
	def __init__(self, pin):
		threading.Thread.__init__(self, name="BBLed_" + str(pin))
		#self.setName('BBLed_' + str(pin))
		self.__pin = pin
		self.__running = False
		self.__led_on = False
		self.__wake_signal = threading.Condition()
		self.__flash_rate = 0.1
		self.__flash_count = 2
		self.__flashing = False
		self.__flashing_rate = 0.2
		
	def flashing(self, b, rate = 0.25):
		with self.__wake_signal:
			self.__flashing = bool(b)
			self.__flashing_rate = rate
			self.__wake_signal.notifyAll()

	def flash(self, count = 2, rate = 0.1):
		with self.__wake_signal:
			self.__flash_count = count
			self.__flash_rate = 0.1
			self.__wake_signal.notifyAll()

	def on(self, b):
		with self.__wake_signal:
			self.__led_on = bool(b)
			self.__wake_signal.notifyAll()

	def stop(self):
		with self.__wake_signal:
			self.__running = False
			self.__wake_signal.notifyAll()

	def run(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__pin, GPIO.OUT, initial=0)
		
		self.__running = True
		
		with self.__wake_signal: # has lock whenever awake
			while self.__running:
				
				while self.__flash_count > 0 and self.__running:
					self.__flash_count -= 1
					GPIO.output(self.__pin, 1)
					self.__wake_signal.wait(self.__flash_rate)
					GPIO.output(self.__pin, 0)
					self.__wake_signal.wait(self.__flash_rate)
				
				while self.__flashing and self.__running:
					GPIO.output(self.__pin, 1)
					self.__wake_signal.wait(self.__flashing_rate)
					GPIO.output(self.__pin, 0)
					self.__wake_signal.wait(self.__flashing_rate)
				
				if not self.__running:
					break
				GPIO.output(self.__pin, self.__led_on)
				self.__wake_signal.wait()
		
		# set pin back to output
		GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)