#!/bin/bash -x

sudo unexpand --tabs=4 $1 > temp.temp
sudo mv $1 $1.bkp
#sudo chown www-data:www-data $1.bkp
sudo mv temp.temp $1
#sudo chown www-data:www-data $1

