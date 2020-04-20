# Serenity HydroPi (SHyPi)

A heavily modified version of dombold's MyHydroPi pool monitor (https://github.com/dombold/MyHydroPi) used for monitoring and alerting on hydroponic grows. Includes a PHP web dashboard with live sensor readings and historical data. Generates email alerts when sensor values read outside of your specified range. Out-of-box support for pH, air temp, and EC sensors, but can be adapted to use many more!

## Demo

https://youtu.be/ri-gNEmVmG0

## Notes

* A Raspberry Pi 4 is recommended due to MySQL using more RAM than the RPi 2 or 3 can handle.
* You may need to manually enable i2c on your RPi. This is easy with the raspi-config terminal command.
* Atlas Scientific brand sensors seemed to work the best in our tests.

## Parts List

https://myhydropi.com/hydropi-parts-list

## Getting Started

These instructions will get you a copy of the SHyPi project up and running on your Raspberry Pi.

### Prerequisites

    apt-get update
    apt-get install -y apache2 php libapache2-mod-php ffmpeg imagemagick mariadb-server-10.0 php-mysql python-mysqldb i2c-tools

    #Permissions
	mkdir /home/pi/SHyPi
	chown www-data:www-data /home/pi/SHyPi/
	chmod 777 /home/pi/SHyPi/

	#MySQL setup
	echo "CREATE DATABASE hydropi;
	USE hydropi;
	CREATE TABLE notes (dateandtime VARCHAR(30),notes VARCHAR(1500)); 
	CREATE TABLE grows (growid INT(11) NOT NULL AUTO_INCREMENT, startdate VARCHAR(12), enddate VARCHAR(12), strainname VARCHAR(25), growername VARCHAR(25), othernotes VARCHAR(1500), PRIMARY KEY (growid));
	GRANT ALL PRIVILEGES ON *.* TO 'serenityadmin'@'localhost' IDENTIFIED BY 'Serenity2019!';
	DELETE FROM mysql.user WHERE User='';
	DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
	DROP DATABASE IF EXISTS test;
	DELETE FROM mysql.db WHERE Db='test';
	FLUSH PRIVILEGES;" >> /home/pi/SHyPi/mysql_secure_install.sql

	mysql -fu root < "/home/pi/SHyPi/mysql_secure_install.sql"

### Installing SHyPi software

	#Install SHyPI source code
	git clone http://10.0.0.93:3000/alan/serenity-hydropi.git /home/pi/SHyPi/src/

	rm -rf /var/www/html/index.html
	cp -r /home/pi/SHyPi/src/html/* /var/www/html/

	chown www-data:www-data /var/www/html/timelapses/
	chmod 777 /var/www/html/timelapses/

	chown www-data:www-data /var/www/html/php/restart.php

	systemctl restart apache2

	#Allow www-data user to reboot machine (from web console buttons)
	echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers

	#Start monitoring script at boot
	(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/SHyPi/src/python2/Serenity-HydroPi.py") | sudo crontab -


### Wiring your Raspberry Pi

Follow the tutorials from: https://myhydropi.com to configure the hardware of your SHyPi.

## Components

* Python script - responsible for continuously reading the sensors and storing the values in the MySQL database. Also handles sending of email alerts to the recepient specified in the Settings page.
* PHP dashboard - pulls values from MySQL and generates historical graphs. Allows the user to create timelapse videos from images captured at every sensor reading.

## Authors

* **Alan Raff** - *Lead Developer* - [LinkedIn](https://www.linkedin.com/in/alan-raff-9a217280)
