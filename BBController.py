import threading
import time
import BBSharedData
import RPi.GPIO as GPIO
from termcolor import colored
from datetime import datetime

def main_thread_running():
	for t in threading.enumerate():
		if t.name == "MainThread" and t.is_alive() == False:
			return False
	return True

class BBController(threading.Thread):
	def __init__(self, data):
		threading.Thread.__init__(self)
		self.data = data
		self.wake_signal = threading.Condition()
		self.running = True
		
		# set constants
		self.GPIO_pin = 21
		self.signal_boiler_on = GPIO.LOW
		self.signal_boiler_off = GPIO.HIGH
		
		# setup gpio pins
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.GPIO_pin, GPIO.OUT, initial=self.signal_boiler_off)
	
	def wake_controller_thread(self):
		with self.wake_signal:
			self.wake_signal.notify()

	# on change mode, try to maintain on/off status
	def set_mode(self, mode):
		if self.data.mode == mode:
			return;
		
		with self.data:
			if mode == "switch":
				self.data.mode = "switch"
			
			elif mode == "count":
				self.data.mode = "count"
				t = int(time.time())
				if self.data.boiler_on:
					if self.data.countdown_off_time < t:
						self.data.countdown_off_time = t + (60 * 60)
				else:
					self.data.countdown_off_time = t
					
			elif mode == "therm":
				self.data.mode = "therm"
		self.wake_controller_thread()

	def switch(self, active):
		with self.data:
			self.data.mode = "switch"
			self.data.boiler_on = (active == True)
			self.data.pending = True
		self.wake_controller_thread()
		
	def count(self, off_time):
		with self.data:
			self.data.mode = "count"
			t = int(time.time())
			# set limits - now, now + 4h
			self.data.countdown_off_time = max(t, min(t+(60 * 60 * 4), int(off_time)))
			self.data.boiler_on = (self.data.countdown_off_time > t)
			self.data.pending = True
		self.wake_controller_thread()
	
	#CHANGE NAME
	def therm(self, temp):
		temp = min(temp, 25.0)
		temp = max(temp, 5.0)
		with self.data:
			self.data.mode = "therm"
			self.data.target_temp = temp
		self.wake_controller_thread()
		
	def thermometer(self, temp):
		self.data.thermometer_temp = temp
		self.data.thermometer_update_time = time.time()
		self.wake_controller_thread()

	def shutdown(self):
		self.running = False # assignments are atomic
		self.wake_controller_thread()
	
	def turn_boiler_on(self):
		print(colored("Boiler on - GPIO " + str(self.GPIO_pin) + " test=" + str(self.data.settings.test_mode), "yellow"))
		if not self.data.settings.test_mode:
			GPIO.output(self.GPIO_pin, self.signal_boiler_on)

	def turn_boiler_off(self):
		print(colored("Boiler off - GPIO " + str(self.GPIO_pin) + " test=" + str(self.data.settings.test_mode), "green"))
		if not self.data.settings.test_mode:
			GPIO.output(self.GPIO_pin, self.signal_boiler_off)

	def run(self):
		self.previous_boiler_state = self.data.boiler_on
		self.previous_change_time = int(time.time())
		
		while self.running:
			current_time = int(time.time())
			print ("BBController.run() -- tick -- " + datetime.fromtimestamp(current_time).strftime('%H:%M:%S'))
			
			if not main_thread_running():
				print (colored("Main thread terminated, shuting down", "red"))
				break;
			
			with self.data:
				if self.data.mode == "switch":
					print ("mode = switch")
					
				elif self.data.mode == "count":
					print ( "mode = count")
					print ("countdown_off_time = ", self.data.countdown_off_time)
					print ("current_time = ", current_time)
					self.data.boiler_on = (self.data.countdown_off_time > current_time)
				
				elif self.data.mode == "therm":
					print ("mode = therm")
					print ("target_temp = ", self.data.target_temp)
					print ("thermometer_temp = ", self.data.thermometer_temp)
					self.data.boiler_on = (self.data.target_temp > self.data.thermometer_temp)
					self.data.boiler_on = False
					
				else:
					print ("mode = unknown")
					self.data.boiler_on = False
				
				boiler_on = self.data.boiler_on
				self.data.pending = False
				
				# test for state change, only change boiler if dt < min switching
				if self.data.boiler_on != self.previous_boiler_state:
					if (current_time - self.previous_change_time) < self.data.settings.min_switching:
						# state change unsuccessful, set pending
						print (colored("Time since last change = " + str(current_time - self.previous_change_time), "blue"))
						print (colored("Boiler state change pending to ... " + str(self.data.boiler_on), "blue"))
						boiler_on = self.previous_boiler_state
						self.data.pending = True
					else:
						# state change successful
						print (colored("Changing boiler state", "blue"))
						self.previous_boiler_state = self.data.boiler_on
						self.previous_change_time = current_time
					
				if boiler_on:
					self.turn_boiler_on()
				else:
					self.turn_boiler_off()
				
			# sleep for tick, but wake up if signalled
			with self.wake_signal:
				self.wake_signal.wait(self.data.settings.controller_tick)
			
					
					
				"""	 
					self.data.boiler_on = False
					for p in self.data.schedule:
						if (p.stop < self.status.time):
							print colored("removing " + str(p), "red")
							self.status.schedule.remove(p)
						elif (p.start <= self.status.time) and (p.stop > self.status.time):
							self.status.boiler_active = True
					
					if self.status.boiler_active:
						self.turn_boiler_on()
					else:
						self.turn_boiler_off()
					
					if self.status.boiler_active != old_boiler_state:
						print colored("Boiler turned %d" % self.status.boiler_active, "blue")
					old_boiler_state = self.status.boiler_active
				print self.status """
		
		print(colored("Controller shuting down", "red"))	   
		# make sure that boiler is off
		self.turn_boiler_off()
		GPIO.cleanup()

if __name__ == "__main__":
	import BBMain
	BBMain.go()
