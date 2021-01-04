#!/bin/bash
#USAGE: sudo bash install.sh

#Update package index
apt-get update -y

#Install dependencies with aptitude
apt-get install -y apache2 php libapache2-mod-php ffmpeg imagemagick mariadb-server-10.0 php-mysql python-mysqldb i2c-tools

#Configure permissions for project directory
mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/ #In a real-world scenario, 777 permissions can be risky, but as this dashboard is not meant to be internet facing the attack surface is greatly reduced

#Generate mysql_secure_install.sql script
echo -e "CREATE DATABASE hydropi;\nUSE hydropi;\nCREATE TABLE notes (dateandtime VARCHAR(30),notes VARCHAR(1500)); \nCREATE TABLE grows (growid INT(11) NOT NULL AUTO_INCREMENT, startdate VARCHAR(12), enddate VARCHAR(12), strainname VARCHAR(25), growername VARCHAR(25), othernotes VARCHAR(1500), PRIMARY KEY (growid));\nGRANT ALL PRIVILEGES ON *.* TO 'serenityadmin'@'localhost' IDENTIFIED BY 'Serenity2019!';\nDELETE FROM mysql.user WHERE User='';\nDELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');\nDROP DATABASE IF EXISTS test;\nDELETE FROM mysql.db WHERE Db='test';\nFLUSH PRIVILEGES;" > /home/pi/SHyPi/mysql_secure_install.sql

#Execute MySQL configuration script
mysql -fu root < "/home/pi/SHyPi/mysql_secure_install.sql"

#Move web dashboard files to apache's www folder
cp -r /home/pi/SHyPi/src/html/* /var/www/html/

#Remove default Apache index page
rm -rf /var/www/html/index.html

#Configure permissions for folder that holds all the generated timelapse videos
chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/

#Allow www-data user to reboot machine (from web console buttons)
chown www-data:www-data /var/www/html/php/restart.php
echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers