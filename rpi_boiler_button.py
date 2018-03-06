import RPi.GPIO as GPIO
import time
import urllib.request

BUTTON_CHANNEL = 3
EDGE_DELAY = 0.10
BOUNCE_THRESHOLD = 1.0
WAIT_TIMEOUT = 10000

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_CHANNEL, GPIO.IN, pull_up_down=GPIO.PUD_UP)

c = 0
print("%d) Waiting for edge ..." % c, flush=True)
while True:
	if GPIO.wait_for_edge(BUTTON_CHANNEL, GPIO.FALLING, timeout=WAIT_TIMEOUT) is None:
		continue
	time.sleep(EDGE_DELAY)
	inp = GPIO.input(BUTTON_CHANNEL)
	print("\tEdge detected, pin = %d" % (inp))
	
	if inp == 0:
		try:
			with urllib.request.urlopen("http://127.0.0.1/toggle/" + str(inp)) as r:
				print("\tRequest -> " + str(r.read()))
		except urllib.error.URLError as e:
			print("\tException sending request", e)
	c += 1
	time.sleep(BOUNCE_THRESHOLD)
	print("%d) Waiting for edge ..." % c, flush=True)

GPIO.cleanup()
print("Clean up done")