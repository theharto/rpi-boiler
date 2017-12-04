#!/bin/bash

echo "terminating..."
curl http://localhost/shutdown

sleep 2

if [ $# -eq 0 ];
then
	echo "starting normally ... "
	sudo python BBMain.py &
else
	echo "starting with nohup ..."
	sudo nohup python BBMain.py >~/bb.log &

fi
