<?php 
	$name = htmlspecialchars($_POST['name']);
	$email = htmlspecialchars($_POST['email']);
	$airtemplow = htmlspecialchars($_POST['airtemplow']);
	$airtemphigh = htmlspecialchars($_POST['airtemphigh']);
	$phlow = htmlspecialchars($_POST['phlow']);
	$phhigh = htmlspecialchars($_POST['phhigh']);

	$file = fopen("/home/pi/SHyPi/SHyPi_web_settings.py", "w") or die("can't open file");
	$data = "user_name_value = '".$name."'\nemail_value = '".$email."'\nairtemplow_value = ".$airtemplow."\nairtemphigh_value = ".$airtemphigh."\nphlow_value = ".$phlow."\nphhigh_value = ".$phhigh;
	fwrite($file, $data);

    // show a success msg 
    echo "data successfully entered";
    fclose($file);
?>