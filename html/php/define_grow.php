<?php
// DEFINE_GROW.PHP
    require "hydropi_connect.php";
    $startdate = htmlspecialchars($_POST['startdate']);
    $enddate = htmlspecialchars($_POST['enddate']);
    $strainname = htmlspecialchars($_POST['strainname']);
    $growername = htmlspecialchars($_POST['growername']);
    $othernotes = htmlspecialchars($_POST['othernotes']);

    $final_startdate = "";
    $final_enddate = "";

    $startdate_array = explode ("/", $startdate);
    $enddate_array = explode ("/", $enddate);

    $final_startdate .= $startdate_array[2];
    $final_startdate .= $startdate_array[0];
    $final_startdate .= $startdate_array[1];
    $final_startdate .= "0000";

    $final_enddate .= $enddate_array[2];
    $final_enddate .= $enddate_array[0];
    $final_enddate .= $enddate_array[1];
    $final_enddate .= "0000";

    $sql = "INSERT INTO grows (startdate, enddate, strainname, growername, othernotes) VALUES (\"".$final_startdate."\",\"".$final_enddate."\",\"".$strainname."\",\"".$growername."\",\"".$othernotes."\"); ";
    if (mysqli_query($conn, $sql)) {
        $url = "Location: http://10.0.0.120/grows.php";
		header($url);
		die();
            } else {
               echo "Error: " . $sql . "" . mysqli_error($conn);
            }
    mysqli_close($conn);
?>