<?php
$year = htmlspecialchars($_POST['year']);
$month = htmlspecialchars($_POST['month']);
$day = htmlspecialchars($_POST['day']);
$filename = htmlspecialchars($_POST['filename']);

$mkvidcmd = "ffmpeg -r 24 -pattern_type glob -i 'camimages/".$year.$month.$day."*.jpg' -vcodec libx264 -pix_fmt yuv420p /home/pi/SHyPi/".$filename.".mp4";
system($mkvidcmd);

$mvvidcmd = "cp /home/pi/SHyPi/".$filename." /var/www/html/timelapses/";
system($mvvidcmd);

?>