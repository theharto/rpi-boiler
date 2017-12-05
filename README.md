# rpi-boiler

## Install nginx and php
https://thepi.io/how-to-set-up-a-web-server-on-the-raspberry-pi/  
sudo apt install nginx  
sudo apt install php-fpm php-zip php-mbstring  

## Install Codiad
sudo mkdir /var/www/html/codiad
sudo git clone https://github.com/Codiad/Codiad /var/www/html/codiad  
sudo touch /var/www/html/codiad/config.php  
sudo chown www-data:www-data -R /var/www/html/codiad/  
