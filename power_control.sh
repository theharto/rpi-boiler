#!/bin/bash

while true; do
	r=$(nc -l 5511)

	if [[ $r == "poweroff" ]]; then
		echo "poweroff"
		poweroff
	elif [[ $r == "reboot" ]]; then
		echo "reboot"
		reboot
	else
		echo -n "Unknown command: "
		echo $r
	fi
done