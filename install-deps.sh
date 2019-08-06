apt-get update
apt-get install -y apache2
apt-get install -y php libapache2-mod-php
apt-get install -y ffmpeg
apt-get install -y imagemagick
apt-get install -y mysql-server php-mysql
apt-get install -y python-mysqldb

sleep(180)

#MySQL
echo "CREATE DATABASE growbox;
USE growbox;
CREATE TABLE notes (dateandtime VARCHAR(30),notes VARCHAR(1500)); 
CREATE TABLE grows (startdate VARCHAR(12), enddate VARCHAR(12), strainname VARCHAR(25), growername VARCHAR(25), othernotes VARCHAR(1500));
GRANT ALL PRIVILEGES ON *.* TO 'grow'@'localhost' IDENTIFIED BY 'Serenity2019!';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test';
FLUSH PRIVILEGES;" >> /home/grow/mysql_secure_install.sql

mysql -fu root < "/home/grow/mysql_secure_install.sql"

#Permissions
mkdir /home/grow/SHyPi
chown www-data:www-data /home/grow/SHyPi/
chmod 777 /home/grow/SHyPi/

chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/

systemctl restart apache2

chown www-data:www-data /var/www/html/php/restart.php

echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers

(sudo crontab -l 2>/dev/null; echo "@reboot python /home/grow/Desktop/Serenity-HydroPi.py") | sudo crontab -

ls /sys/bus/w1/devices/ #find DS18B20 temp sensor device id