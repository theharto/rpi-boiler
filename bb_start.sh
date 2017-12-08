#!/bin/bash

echo "terminating..."
curl http://localhost/shutdown

sleep 2

if [ $# -eq 0 ];
then
	echo "starting normally ... "
	python3 BBMain.py &
else
	echo "starting with nohup ..."
	nohup python3 BBMain.py > bb.log &
fi
