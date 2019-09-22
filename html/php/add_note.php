<?php
// ADD_NOTE.PHP
    require "hydropi_connect.php";
    $dateandtime = htmlspecialchars($_POST['dateandtime']);
	$notes = htmlspecialchars($_POST['notes']);

    $sql = "INSERT INTO notes (dateandtime, notes) VALUES (\"".$dateandtime."\",\"".$notes."\"); ";
    if (mysqli_query($conn, $sql)) {
        $url = "Location: http://192.168.1.101/notes.php";
		header($url);
		die();
            } else {
               echo "Error: " . $sql . "" . mysqli_error($conn);
            }
    mysqli_close($conn);
?>