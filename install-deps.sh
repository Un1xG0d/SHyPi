apt-get update
apt-get install -y apache2
apt-get install -y php libapache2-mod-php
apt-get install -y mysql-server php-mysql
apt-get install -y python-mysqldb

mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/