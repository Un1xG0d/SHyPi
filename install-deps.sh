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
CREATE TABLE grows (growid INT(11) NOT NULL AUTO_INCREMENT, startdate VARCHAR(12), enddate VARCHAR(12), strainname VARCHAR(25), growername VARCHAR(25), othernotes VARCHAR(1500), PRIMARY KEY (growid));
GRANT ALL PRIVILEGES ON *.* TO 'grow'@'localhost' IDENTIFIED BY 'Serenity2019!';
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test';
FLUSH PRIVILEGES;" >> /home/pi/mysql_secure_install.sql
sleep(3)
mysql -fu root < "/home/pi/mysql_secure_install.sql"

#Permissions
mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/

#Install SHyPI source code
git clone http://10.0.0.93:3000/alan/serenity-hydropi.git /home/pi/SHyPi/src/
sleep(10)
cp -r /home/pi/SHyPi/src/html/* /var/www/html/

chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/

systemctl restart apache2

chown www-data:www-data /var/www/html/php/restart.php

echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers

(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/Desktop/Serenity-HydroPi.py") | sudo crontab -