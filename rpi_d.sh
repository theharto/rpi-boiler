#!/bin/bash

echo "-- rpi-boiler startup script --"

if [[ $# -eq 0 ]]; then
	echo "Usage: ./rpi_d.sh start|stop [stdout]"
	exit 1
fi

echo "Terminating existing process ..."
curl http://127.0.0.1/shutdown > /dev/null 2>&1

if [[ $1 == 'start' ]]; then
	sleep 1
	cd /home/pi/rpi-boiler
	echo "creating wireless link..."
	ln -s -f /proc/net/wireless &
	
	if [[ $2 == 'null_out' ]]; then
		echo "Starting (null_out) ..."
		python3 BBMain.py $3 $4 > /dev/null 2>&1 &
	else
		echo "Starting ..."
		python3 BBMain.py $2 $3 &
	fi
fi

echo "-- exit rpi-boiler startup script --"
