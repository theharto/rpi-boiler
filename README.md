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

## Add sock file
- sudo mkdir /run/rpi-boiler
- sudo chown www-data:www-data /run/rpi-boiler
- sudo chmod 777 /run/rpi-boiler

