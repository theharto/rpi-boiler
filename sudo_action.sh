#!/bin/bash

while true; do
	r=$(nc -l 127.0.0.1 5511)
	
	echo -n `date +"%D %T"`
	
	if [[ $r == "poweroff" ]]; then
		echo " poweroff"
		sudo shutdown -P now
	elif [[ $r == "reboot" ]]; then
		echo " reboot"
		sudo shutdown -r now
	else
		echo -n " Unknown command: "
		echo $r
	fi
done