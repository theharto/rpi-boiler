# rpi-boiler

## Install python3 and pip3 and pip

## Install nginx and php
https://thepi.io/how-to-set-up-a-web-server-on-the-raspberry-pi/  
- sudo apt install nginx  
- sudo apt install php-fpm php-zip php-mbstring  

## Install Codiad
- sudo mkdir /var/www/html/codiad
- sudo git clone https://github.com/Codiad/Codiad /var/www/html/codiad  
- sudo touch /var/www/html/codiad/config.php  
- sudo chown www-data:www-data -R /var/www/html/codiad/
- add link from /var/www/html/codiad/workspace/rpi-boiler to rpi-boiler directory

## Setup git  
- Add project in codiad from git repo  
- In terminal plugin  
  - git config --global user.name "John Doe"  
  - git config --global user.email johndoe@example.com  
  - git remote add origin https://theharto:[PASSWORD]@github.com/theharto/rpi-boiler.git  

## Easy backup and restore from GitHub  
- github_backup.sh  
- github_restore.sh  

## Install bjoern  
- sudo apt install libev-dev  
- sudo pip3 install bjoern  

## Run from cron
sudo crontab -e -u www-data
@reboot /home/pi/rpi-boiler/rpi_d.sh start

sudo crontab -e
@reboot sudo /home/pi/rpi-boiler/sudo_action.sh >> /home/pi/rpi-boiler/logs/sa.log 2>&1

## add link to wireless
ln -s -f /proc/net/wireless wireless