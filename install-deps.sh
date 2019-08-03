apt-get update
apt-get install -y apache2
apt-get install -y php libapache2-mod-php
apt-get install -y ffmpeg
apt-get install -y imagemagick
apt-get install -y mysql-server php-mysql
apt-get install -y python-mysqldb

mkdir /home/pi/SHyPi
chown www-data:www-data /home/pi/SHyPi/
chmod 777 /home/pi/SHyPi/

chown www-data:www-data /var/www/html/timelapses/
chmod 777 /var/www/html/timelapses/

systemctl restart apache2

chown www-data:www-data /var/www/html/php/restart.php

echo "www-data	ALL=(root) NOPASSWD: /sbin/reboot, /sbin/poweroff" >> /etc/sudoers

(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/Desktop/Serenity-HydroPi.py") | sudo crontab -