<?php
// INITIAL_SETTINGS_DATA.PHP
    // Get all the settings names from the database
    include "php/settings_col_names.php";
    require "php/hydropi_connect.php";
    foreach ($colnames as $title) {
        $sql= ("SELECT ".$title." FROM settings WHERE pk = 1 ");
        $result = mysqli_query($conn, $sql);
        $row = mysqli_fetch_row($result);
        // Write settings values to the webpage
        if ($title == "ds18b20_temp_hi" || $title == "ds18b20_temp_low" || $title == "atlas_temp_hi" || $title == "atlas_temp_low") {
            echo"document.getElementById(\"" .$title. "\").value = \"".$row[0]."\";\n";
        } else {
            echo"document.getElementById(\"" .$title. "\").value = \"".$row[0]."\";\n";
        }
    }
    mysqli_free_result($result);
    mysqli_close($conn);
?>