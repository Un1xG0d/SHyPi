apt-get update
apt-get install -y apache2
apt-get install -y php libapache2-mod-php
apt-get install -y ffmpeg
apt-get install -y imagemagick
apt-get install -y mariadb-server-10.0 php-mysql
apt-get install -y python-mysqldb
apt-get install -y i2c-tools

sleep 180

#Permissions
mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/

#MySQL
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
sleep 3
mysql -fu root < "/home/pi/SHyPi/mysql_secure_install.sql"

#Install SHyPI source code
git clone http://10.0.0.93:3000/alan/serenity-hydropi.git /home/pi/SHyPi/src/
sleep 10
rm -rf /var/www/html/index.html
cp -r /home/pi/SHyPi/src/html/* /var/www/html/

chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/

chown www-data:www-data /var/www/html/php/restart.php

systemctl restart apache2


#echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers

#(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/SHyPi/src/python2/Serenity-HydroPi.py") | sudo crontab -
