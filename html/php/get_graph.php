<?php
// GET_GRAPH.PHP
    require "hydropi_connect.php";
    function clean($string) {
       $string = str_replace(' ', '', $string); // remove whitespaces

       return preg_replace('/[^A-Za-z0-9\-]/', '', $string); // Removes special chars.
    }
    // Read variables from AJAX call
    $timeframe = $_POST['newtimeframe'];
    $sensor_name = $_POST['sensor'];
    $label_name = $_POST['label'];
    // Get the sensor readings for the selected timeframe
    $sql = "SELECT timestamp, ".$sensor_name." from sensors where timestamp > now() - interval '".$timeframe."' day";
    $result = mysqli_query($conn, $sql);
    $row = mysqli_fetch_row($result);

    $table = array();
    $table['cols'] = array(
        array('label' => 'Date', 'type' => 'string'),
        array('label' => $label_name, 'type' => 'number'),
        array('label' => 'Img_URL', 'type' => 'string', 'role' => 'annotationText')
        );
    $rows = array();

    foreach($result as $row){
        // Build array for google chart
        $time = strtotime($row['timestamp']);
        $short_date = date("Y/m/d H:i", $time); //same format as picture filenames
        $temp = array();
        $date_sanitized = clean($short_date);
        //$date_link = "<a href='camimages/".$date_sanitized.".jpg'>".$short_date."</a>";
        $date_link = "camimages/".$date_sanitized.".jpg";

        if ($sensor_name == "ds18b20_temp") {
            //Value
            $c = $row[$sensor_name];
            $f = ($c * 9/5) + 32;
            $temp[] = array('v' => (string) $short_date);
            $temp[] = array('v' => (float) round($f,2));
            $temp[] = array('v' => (string) $date_link);
            $rows[] = array('c' => $temp);
        } else {
            //Value
            $temp[] = array('v' => (string) $short_date);
            $temp[] = array('v' => (float) round($row[$sensor_name],2));
            $temp[] = array('v' => (string) $date_link);
            $rows[] = array('c' => $temp);
        }

        
    }
    $result->free();
    $table['rows'] = $rows;
    $jsonTable = json_encode($table, true);
    // Return array to javascript for google chart
    echo json_encode($table, JSON_PRETTY_PRINT);

    mysqli_close($conn);
?>