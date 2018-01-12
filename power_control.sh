#!/bin/bash

while true; do
	r=$(nc -l localhost 5511)
	
	if [[ $r == "poweroff" ]]; then
		echo `date +"%D %T"` poweroff
		sudo shutdown -P now
	elif [[ $r == "reboot" ]]; then
		echo `date +"%D %T"` reboot
		sudo shutdown -r now
	else
		echo -n `date +"%D %T"` "Unknown command: "
		echo $r
	fi
done