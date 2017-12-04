#!/bin/bash -x

sudo unexpand --tabs=4 $1 > temp.temp
sudo cp $1 $1.bkp
sudo chown www-data:www-data $1.bkp
sudo cp temp.temp $1
sudo chown www-data:www-data $1

