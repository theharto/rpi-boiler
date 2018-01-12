#!/bin/bash

echo "-- rpi-boiler startup script --"

if [[ $# -eq 0 ]]; then
	echo "Usage: ./rpi_d.sh start|stop [stdout]"
	exit 1
fi

echo "Terminating existing process..."
curl http://localhost/shutdown &> /dev/null

cd /home/pi/rpi-boiler

if [[ $1 == 'start' ]]; then
	sleep 1
	if [[ $2 == 'stdout' ]]; then
		echo "Starting - output to stdout ..."
		python3 BBMain.py &
	else
		echo "Starting ..."
		python3 BBMain.py &> bb_err.log &
	fi
fi
