<?php
$year = htmlspecialchars($_POST['year']);
$month = htmlspecialchars($_POST['month']);
$day = htmlspecialchars($_POST['day']);
$filename = htmlspecialchars($_POST['filename']);

$mkvidcmd = "ffmpeg -r 24 -pattern_type glob -i 'camimages/".$year.$month.$day."*.jpg' -vcodec libx264 -pix_fmt yuv420p /var/www/html/timelapses/".$filename.".mp4";
system($mkvidcmd);

$url = "Location: http://10.0.0.153/timelapses/".$filename.".mp4";
header($url);
die();

?>