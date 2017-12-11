import RPi.GPIO as GPIO
import os

SWITCH_GPIO = 5

GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try :
	r = GPIO.wait_for_edge(SWITCH_GPIO, GPIO.BOTH)

	print("gpio_shutdown.py> Shutdown switch detected " + r)
	os.system("sudo echo 'hi there'")
	#os.system("sudo poweroff")
except:
	print("gpio_shutdown.py> Exception")

print("gpio_shutdown.py> ending")
GPIO.cleanup()