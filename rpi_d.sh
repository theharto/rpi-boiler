#!/bin/bash

echo "-- rpi-boiler startup script --"

if [[ $# -eq 0 ]]; then
	echo "Usage: ./rpi_d.sh start|stop [stdout]"
	exit 1
fi

echo "Terminating existing process..."
curl https://homefire.cf/shutdown &> /dev/null


if [[ $1 == 'start' ]]; then
	sleep 1
	cd /home/pi/rpi-boiler
	echo "creating wireless link..."
	ln -s -f /proc/net/wireless
	echo "Starting..."
	python3 BBMain.py $2 $3 &
fi

echo "-- exit rpi-boiler startup script --"
