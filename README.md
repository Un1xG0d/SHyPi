# HydroPi Developer Documentation
## Overview
This project is intended for monitoring and alerting on hydroponic grow data. It is deployed on a Raspberry Pi and includes a PHP web dashboard that displays live sensor readings and historical data. The app generates email alerts when the value of a sensor reads outside of the range you specify in the Settings page. This project has out-of-box support for pH, air temp, and EC sensors, but can be adapted to use many more!
- - - -
## Demo
[WATCH DEMO VIDEO](https://youtu.be/ri-gNEmVmG0)
- - - -
## Notes
* This project is a work in progress, and is not yet intended to be used in a large scale production.
* A Raspberry Pi 4 is recommended due to MySQL using more RAM than the RPi 2 or 3 can handle.
* You may need to manually enable i2c on your RPi. This is easy with the `raspi-config`  terminal command.
* Atlas Scientific brand sensors seemed to work the best in our tests.
- - - -
## Parts List
https://myhydropi.com/hydropi-parts-list
- - - -
## Getting Started (Software)
### Prerequisites
#### Install Dependencies
```
apt-get install -y apache2 php libapache2-mod-php ffmpeg imagemagick mariadb-server-10.0 php-mysql python-mysqldb i2c-tools
```

#### Configure File Permissions
```
mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/
```

#### Create MySQL Configuration Script
> /home/pi/SHyPi/mysql_secure_install.sql

```
CREATE DATABASE hydropi;
USE hydropi;
CREATE TABLE notes (dateandtime VARCHAR(30),notes VARCHAR(1500)); 
CREATE TABLE grows (growid INT(11) NOT NULL AUTO_INCREMENT, startdate VARCHAR(12), enddate VARCHAR(12), strainname VARCHAR(25), growername VARCHAR(25), othernotes VARCHAR(1500), PRIMARY KEY (growid));
GRANT ALL PRIVILEGES ON *.* TO 'serenityadmin'@'localhost' IDENTIFIED BY 'Serenity2019!';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test';
FLUSH PRIVILEGES;
```

#### Execute MySQL Configuration Script
```
mysql -fu root < "/home/pi/SHyPi/mysql_secure_install.sql"
```

### Installing SHyPi software
#### Clone the project source code to your RPi
```
git clone https://github.com/psycoder17/SHyPi.git /home/pi/SHyPi/src/
cp -r /home/pi/SHyPi/src/html/* /var/www/html/
```

#### Remove default Apache index page
```
rm -rf /var/www/html/index.html
```

#### Configure File Permissions
```
chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/
```

#### Allow www-data user to reboot machine (from web console buttons)
```
chown www-data:www-data /var/www/html/php/restart.php
echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers
```

#### Create cronjob to run monitoring script at boot
```
(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/SHyPi/src/python2/Serenity-HydroPi.py") | sudo crontab -
```
- - - -
## Wiring your Raspberry Pi
Follow the tutorials at https://myhydropi.com to attach the sensors and configure the hardware of your SHyPi.
[Connecting pH sensor](https://myhydropi.com/connecting-a-ph-sensor-to-a-raspberry-pi)
[Connecting air temp sensor](https://myhydropi.com/ds18b20-temperature-sensor-on-a-raspberry-pi)
[Connecting EC sensor](https://myhydropi.com/connecting-an-electrical-conductivity-sensor-to-a-raspberry-pi)
- - - -
## Project Components
### Python script:
	* Responsible for continuously reading the attached sensors and storing the values in the MySQL database. 
	* Handles sending of email alerts when a sensor value is above/below your desired setting.
### PHP dashboard
	* Pulls values from MySQL and generates historical graphs of your sensor data. 
	* Allows the user to create timelapse videos from images captured at every sensor reading. 
	* User can change their sensor thresholds and email alerting preferences on the Settings page.
- - - -
## Resources
### SHyPi Source Code
[SHyPi Source Code](https://github.com/psycoder17/SHyPi)

### Dombold’s MyHydroPi
[Base Project Guide](https://myhydropi.com)
[Base Project Github](https://github.com/dombold/MyHydroPi)