<?php
// GET_NOTES.PHP
    require "hydropi_connect.php";
    // Get all notes from Notes table in MySQL
    $sql = "SELECT * FROM notes;";
    $result = mysqli_query($conn, $sql);
    if (mysqli_num_rows($result) > 0) {
        // output data of each row
        $arr = array();
        while($row = mysqli_fetch_assoc($result)) {
            array_push($arr, array($row['dateandtime'], $row['notes']));
        }
    }
    //print_r(array_values($arr));
    mysqli_free_result($result);
    mysqli_close($conn);
?>