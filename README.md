# HydroPi Developer Documentation
## Overview
This project is intended for monitoring and alerting on hydroponic grow data. It is deployed on a Raspberry Pi and includes a PHP web dashboard that displays live sensor readings and historical data. The app generates email alerts when the value of a sensor reads outside of the range you specify in the Settings page. This project has out-of-box support for pH, air temp, and EC sensors, but can be adapted to use many more!
- - - -
## Demo
[WATCH DEMO VIDEO](https://youtu.be/ri-gNEmVmG0)
- - - -
## Notes
* This project is a work in progress, and is not yet intended to be used in a large scale production.
* A Raspberry Pi 4 is recommended due to MySQL using more RAM than the RPi 2 or 3 can handle.
* You may need to manually enable i2c on your RPi. This is easy with the `raspi-config`  terminal command.
* Atlas Scientific brand sensors seemed to work the best in our tests.
- - - -
## Parts List
https://myhydropi.com/hydropi-parts-list
- - - -
## Install SHyPi software
### Clone the project source code to your Raspberry Pi
```
git clone https://github.com/psycoder17/SHyPi.git /home/pi/SHyPi/src/
```

### Run `install.sh` script to automatically configure your RPi to run this project
```
sudo bash /home/pi/SHyPi/src/install.sh
```

### Create cronjob to run monitoring script at boot
```
(sudo crontab -l 2>/dev/null; echo "@reboot python /home/pi/SHyPi/src/python2/Serenity-HydroPi.py") | sudo crontab -
```
- - - -
## Wiring your Raspberry Pi
Follow the tutorials at https://myhydropi.com to attach the sensors and configure the hardware of your SHyPi.

[Connecting pH sensor](https://myhydropi.com/connecting-a-ph-sensor-to-a-raspberry-pi)

[Connecting air temp sensor](https://myhydropi.com/ds18b20-temperature-sensor-on-a-raspberry-pi)

[Connecting EC sensor](https://myhydropi.com/connecting-an-electrical-conductivity-sensor-to-a-raspberry-pi)
- - - -
## Project Components
### Python script:
	* Responsible for continuously reading the attached sensors and storing the values in the MySQL database. 
	* Handles sending of email alerts when a sensor value is above/below your desired setting.
### PHP dashboard
	* Pulls values from MySQL and generates historical graphs of your sensor data. 
	* Allows the user to create timelapse videos from images captured at every sensor reading. 
	* User can change their sensor thresholds and email alerting preferences on the Settings page.
- - - -
## Resources
### Dombold’s MyHydroPi
[Base Project Guide](https://myhydropi.com)

[Base Project Github](https://github.com/dombold/MyHydroPi)