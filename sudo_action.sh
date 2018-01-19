#!/bin/bash

while true; do
	r=$(nc -l 127.0.0.1 5511)
	
	echo -n `date +"%D %T"`
	echo -n " "
	
	if [[ $r == "poweroff" ]]; then
		echo "poweroff"
		sudo shutdown -P now
	
	elif [[ $r == "reboot" ]]; then
		echo "reboot"
		sudo shutdown -r now
	
	elif [[ $r == "stop_net" ]]; then
		echo "stopping network"
		sudo ip link set wlan0 down
	
	elif [[ $r == "start_net" ]]; then
		echo "starting network"
		sudo ip link set wlan0 up
	
	else
		echo -n " Unknown command: "
		echo $r
	fi
done