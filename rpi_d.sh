#!/bin/bash

echo "-- rpi-boiler daemon --"

cd /var/www/html/codiad/workspace/rpi-boiler

if [[ $# -eq 0 ]]; then
	echo "Usage: ./rpi_d.sh start|stop [nohup]"
	exit 1
fi

echo "Terminating existing process..."
curl http://localhost/shutdown > /dev/null 2>&1

if [[ $1 == 'start' ]]; then
	sleep 1
	if [[ $2 == 'nohup' ]]; then
		echo "Starting with nohup ..."
		nohup python3 BBMain.py > bb.log &
	else
		echo "Starting ..."
		python3 BBMain.py &
	fi
fi
