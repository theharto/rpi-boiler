import urllib.request
import time
import math
import os
import RPi.GPIO as GPIO

delay = 2.0
url = "https://io.adafruit.com/api/groups/ping-test/send.json?x-aio-key=81e3da45dd1c48bfbdeabb48a3ce5245&"

print("-- webping.py --")
print("Delay = ", delay, "s", sep="")
print("Url =", url)
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
GPIO.setup(21, GPIO.OUT)
GPIO.output(21, GPIO.LOW)

def wifi_strength(max_strength=70.0):
	with open("/proc/net/wireless") as f:
		f.readline()
		f.readline()
		l = f.readline().split()
		if not l:
			return 0
		return int(100.0 * (float(l[2]) / max_strength))

try:
	while 1:
		time.sleep(delay)
		GPIO.output(21, GPIO.HIGH)
		s = wifi_strength()
		u = url + "ping-test.zerow=%d" % s
		print(u)
		r = urllib.request.urlopen(u).read()
		GPIO.output(21, GPIO.LOW)
except:
	print("<!>")

GPIO.cleanup()
print("-- Exiting cleanly --")
