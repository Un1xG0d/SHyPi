<?php
// UPDATE_SETTINGS.PHP
    // Get all the settings names from the database
    include "settings_col_names.php";
    require "hydropi_connect.php";
    foreach ($colnames as $title) {
        $setting = $_POST{"$title"};

        if (empty($setting)){
            // Enter NULL for settings that are left empty
            $setting = "NULL";
            $sql = "UPDATE settings SET ".$title." = ".$setting." WHERE pk = 1";
            $result = mysqli_query($conn, $sql);
            mysqli_free_result($result);
        }
        else if ($title == "ds18b20_temp_hi" || $title == "ds18b20_temp_low" || $title == "atlas_temp_hi" || $title == "atlas_temp_low"){
            // convert F to C when updating settings for any temp sensors
            $f = $setting;
            $c = ($f - 32) / 1.8;
            $sql = "UPDATE settings SET ".$title." = ".$c." WHERE pk = 1";
            $result = mysqli_query($conn, $sql);
            mysqli_free_result($result);
        }
        else if ($title != "to_email"){
            // Update setting value if it isn't to_email
            $sql = "UPDATE settings SET ".$title." = ".$setting." WHERE pk = 1";
            $result = mysqli_query($conn, $sql);
            mysqli_free_result($result);
        }
        else if ($title == "to_email"){
            // Update to_email setting in quotes to provide a string (required for more than one email address)
            $sql = "UPDATE settings SET to_email = \"" .$setting. "\" WHERE pk = 1";
            $result = mysqli_query($conn, $sql);
            mysqli_free_result($result);
        }
    }
    mysqli_close($conn);
    // Alert the user that the settings in the database have been updated
    echo "<script>alert('Settings Updated');document.location='/settings.php'</script>";
?>