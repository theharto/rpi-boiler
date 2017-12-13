import RPi.GPIO as GPIO
import time, threading

class BBLed(threading.Thread):
	
	def __init__(self, pin):
		threading.Thread.__init__(self)
		self.__pin = pin
		self.__running = False
		self.__led_on = False
		self.__led_flash = False
		self.__wake_signal = threading.Condition()
		self.flash_num = 5
		self.flash_rate = 0.04
		
	def set_pin(self, pin):
		print("set pin")
		GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		self.__pin = pin
		GPIO.setup(self.__pin, GPIO.OUT, initial=0)

	def wake(self):
		with self.__wake_signal:
			self.__wake_signal.notify()

	def flash(self):
		print("flash")
		self.__led_flash = True
		self.wake()
	
	def on(self, b):
		print("on ", b)
		self.__led_on = bool(b)
	
	def stop(self):
		print("led stop")
		self.__running = False
	
	def run(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.__pin, GPIO.OUT, initial=0)
		
		self.__running = True
		while self.__running:
			print("Led awake")
			
			if self.__led_flash:
				for i in range(0, self.flash_num):
					GPIO.output(self.__pin, 1)
					time.sleep(self.flash_rate)
					GPIO.output(self.__pin, 0)
					time.sleep(self.flash_rate)
				self.__led_flash = False
			
			GPIO.output(self.__pin, self.__led_on)
			
			with self.__wake_signal:
				self.__wake_signal.wait()
			
		# set pin back to output
		GPIO.setup(self.__pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
