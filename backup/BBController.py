import threading
import time
from BBSharedData import *
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
        print "BBController.init(", self, ")"
        self.data = data
        self.wake_signal = Condition()
        self.running = True
        
        # set constants
        self.GPIO_pin = 2
        self.signal_boiler_on = GPIO.LOW
        self.signal_boiler_off = GPIO.HIGH
        
        # setup gpio pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_pin, GPIO.OUT, initial=self.signal_boiler_off)
    
    def wake_controller_thread(self):
        with self.wake_signal:
            self.wake_signal.notify()

    def set_mode(self, mode):
        with self.data:
            if mode == "switch":
                self.data.mode = "switch"
            elif mode == "count":
                self.data.mode = "count"
            elif mode == "therm":
                self.data.mode = "therm"
        self.wake_controller_thread()

    def switch(self, active):
        with self.data:
            self.data.mode = "switch"
            self.data.boiler_on = (active == True)
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
        print colored("Boiler on - GPIO " + str(self.GPIO_pin) + ":" + self.data.test_mode, "yellow")
        if not self.data.test_mode:
            GPIO.output(self.GPIO_pin, self.signal_boiler_on)

    def turn_boiler_off(self):
        print colored("Boiler off - GPIO " + str(self.GPIO_pin) + ":" + self.data.test_mode, "green")
        if not self.data.test_mode:
            GPIO.output(self.GPIO_pin, self.signal_boiler_off)

    def run(self):
        old_boiler_state = self.data.boiler_on
        
        while self.running:
            print "BBController.run() -- tick -- " + datetime.fromtimestamp(time.time()).strftime('%H:%M:%S')
            
            if not main_thread_running():
                print colored("Main thread terminated, shuting down", "red")
                break;
            
            with self.data:
                if self.data.mode == "switch":
                    print "mode = switch"
                    
                elif self.data.mode == "count":
                    print "mode = count"
                    self.data.boiler_on = False
                
                elif self.data.mode == "therm":
                    print "mode = therm"
                    print "target temp = ", self.data.target_temp
                    print "thermometer_temp = ", self.data.thermometer_temp
                    self.data.boiler_on = (self.data.thermometer_temp < self.data.target_temp)
                    
                else:
                    print "mode = unknown"
                    self.data.boiler_on = False
                    
                if self.data.boiler_on:
                    self.turn_boiler_on()
                else:
                    self.turn_boiler_off()
                
            # sleep for tick, but wake up if signalled
            with self.wake_signal:
                self.wake_signal.wait(self.data.controller_tick)
            
                    
                    
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
        
        print colored("Controller shuting down", "red")        
        # make sure that boiler is off
        self.turn_boiler_off()
        GPIO.cleanup()

if __name__ == "__main__":
    import BBMain
    BBMain.go()
