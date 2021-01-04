<?php
$startdate = htmlspecialchars($_POST['startdate']);
$enddate = htmlspecialchars($_POST['enddate']);
$filename = htmlspecialchars($_POST['filename']);

$final_startdate = "";
$final_enddate = "";

$startdate_array = explode ("/", $startdate);
$enddate_array = explode ("/", $enddate);

$final_startdate .= $startdate_array[2];
$final_startdate .= $startdate_array[0];
$final_startdate .= $startdate_array[1];

$final_enddate .= $enddate_array[2];
$final_enddate .= $enddate_array[0];
$final_enddate .= $enddate_array[1];

//$mkvidcmd = "ffmpeg -r 24 -pattern_type glob -i 'camimages/".$final_startdate."*.jpg' -vcodec libx264 -pix_fmt rgba /var/www/html/timelapses/".$filename.".mp4";
$mkvidcmd = "ffmpeg -r 24 -pattern_type glob -i 'camimages/*.jpg' -vcodec libx264 -pix_fmt rgba /var/www/html/timelapses/".$filename.".mp4";
system($mkvidcmd);

$url = "Location: http://localhost/timelapses/".$filename.".mp4";
header($url);
die();

?>