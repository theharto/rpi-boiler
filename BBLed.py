import RPi.GPIO as GPIO
import time, threading

class BBLed(threading.Thread):
	
	def __init__(self, pin):
		threading.Thread.__init__(self)
		self.pin = pin
		self.running = False
		self.led_on = False
		self.led_flash = False
		self.flash_num = 5
		self.flash_rate = 0.04
		self.wake_signal = threading.Condition()
		
	def set_pin(self, pin):
		print("set pin")
		if self.pin != 0:
			GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		
		if pin != 0:
			GPIO.setup(self.pin, GPIO.OUT, initial=0)
		self.pin = pin

	def wake(self):
		with self.wake_signal:
			self.wake_signal.notify()

	def flash(self):
		print("flash")
		self.led_flash = True
		self.wake()
	
	def on(self):
		print("on")
		self.led_on = True
		self.wake()
	
	def off(self):
		print("off")
		self.led_on = False
		self.wake()
	
	def stop(self):
		print("led stop")
		self.running = False
	
	def run(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin, GPIO.OUT, initial=0)
		
		self.running = True
		while self.running:
			print("Led awake")
			
			if self.led_flash:
				for i in range(0, self.flash_num):
					GPIO.output(self.pin, 1)
					time.sleep(self.flash_rate)
					GPIO.output(self.pin, 0)
					time.sleep(self.flash_rate)
				self.led_flash = False
			
			GPIO.output(self.pin, self.led_on)
			
			with self.wake_signal:
				self.wake_signal.wait()
			
		# set pin back to output
		GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
