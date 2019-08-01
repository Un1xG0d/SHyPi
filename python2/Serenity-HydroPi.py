#!/usr/bin/env python

##############################################################################
#
# Serenity 2019
#
# 1. Read Multiple Sensors - DS18B20 1-wire type Temperature sensors, Atlas
# Scientific Temperature, pH, Oxidation Reduction Potential (ORP) and
# Electrical Conductivity sensors and save the results to a MySQL database at
# a set interval with a set level of accuracy. Multiple sensors of the same
# type can also be used by configuring the "sensors" variable with the correct
# sensor type. A reference temperature reading will be set by one of the
# temperature sensors if any are connected, if not a value of 25C will be
# applied. This is necessary to ensure accurate readings from the other
# sensors as the liquid being tested changes temperature.
# The electrical conductivity reading is also converted to parts per million.
# There is also a customizible "pause" setting included to stop readings while
# chemicals are being added, this prevents spikes in the readings for more
# accurate results.
#
# 2. The program will also create the initial database and tables if they do
# not already exist in MySQL.
#
##############################################################################

import io
import os
import sys
import fcntl
import MySQLdb
import MySQLdb.cursors
from time import sleep
from collections import OrderedDict
import pygame
import pygame.camera
import datetime
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
import smtplib
sys.path.insert(1, '/home/pi/SHyPi/') # insert at 1, 0 is the script path (or '' in REPL)
from SHyPi_web_settings import * # import user-set variables (setupone.php) 
import socket

# Uncomment sleep if running program at startup with crontab
#sleep(10)

# Load Raspberry Pi Drivers for 1-Wire Temperature Sensor

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Define Atlas Scientific Sensor Class


class atlas_i2c:

    long_timeout = 1.5  # the timeout needed to query readings & calibrations
    short_timeout = .5  # timeout for regular commands
    default_bus = 1  # the default bus for I2C on the newer Raspberry Pis,
                     # certain older boards use bus 0
    default_address = 102  # the default address for the Temperature sensor

    def __init__(self, address=default_address, bus=default_bus):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with the bus
        # it is usually 1, except for older revisions where its 0
        # wb and rb indicate binary read and write
        self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

        # initializes I2C to either a user specified or default address
        self.set_i2c_address(address)

    def set_i2c_address(self, addr):
        # set the I2C communications to the slave specified by the address
        # The commands for I2C dev using the ioctl functions are specified in
        # the i2c-dev.h file from i2c-tools
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)

    def write(self, string):
        # appends the null character and sends the string over I2C
        string += "\00"
        self.file_write.write(string)

    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C,
        # then parses and displays the result
        res = self.file_read.read(num_of_bytes)  # read from the board
        # remove the null characters to get the response
        response = filter(lambda x: x != '\x00', res)

        if(ord(response[0]) == 1):  # if the response isnt an error
            # change MSB to 0 for all received characters except the first
            # and get a list of characters
            char_list = map(lambda x: chr(ord(x) & ~0x80), list(response[1:]))
            # NOTE: having to change the MSB to 0 is a glitch in the
            # raspberry pi, and you shouldn't have to do this!
            # convert the char list to a string and returns it
            return ''.join(char_list)
        else:
            return "Error " + str(ord(response[0]))

    def query(self, string):
        # write a command to the board, wait the correct timeout,
        # and read the response
        self.write(string)

        # the read and calibration commands require a longer timeout
        if((string.upper().startswith("R")) or
           (string.upper().startswith("CAL"))):
            sleep(self.long_timeout)
        elif((string.upper().startswith("SLEEP"))):
            return "sleep mode"
        else:
            sleep(self.short_timeout)
        return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()


# Check that only one Primary Temperature sensor is defined


def check_for_only_one_reference_temperature():

    ref_check = 0

    for key, value in sensors.items():
        if (value["is_connected"]) is True:
            if value["sensor_type"] == "1_wire_temp":
                if value["is_ref"] is True:
                    ref_check += 1
            if value["sensor_type"] == "atlas_temp":
                if value["is_ref"] is True:
                    ref_check += 1
    if ref_check > 1:
        os.system('clear')
        print ("\n\n                     !!!! WARNING !!!!\n\n"
        "You can only have one Primary Temperature sensor, Please set the\n"
        "Temperature sensor that is in the liquid you are testing to True\n"
        "and the other to False\n\n                     !!!! WARNING !!!!\n\n")
        sys.exit()  # Stop program
    return

# Create required database in the MySQL if it doesn't' already exist


def create_database():

    conn = MySQLdb.connect(servername, username, password)
    curs = conn.cursor()
    curs.execute("SET sql_notes = 0; ")  # Hide Warnings

    curs.execute("CREATE DATABASE IF NOT EXISTS {}".format(dbname))

    curs.execute("SET sql_notes = 1; ")  # Show Warnings
    conn.commit()
    conn.close()
    return


def open_database_connection():

    conn = MySQLdb.connect(servername, username, password, dbname)
    curs = conn.cursor()
    curs.execute("SET sql_notes = 0; ")  # Hide Warnings

    return conn, curs


def close_database_connection(conn, curs):

    curs.execute("SET sql_notes = 1; ")
    conn.commit()
    conn.close()


def create_sensors_table():

    conn, curs = open_database_connection()

    curs.execute("CREATE TABLE IF NOT EXISTS sensors (timestamp DATETIME);")

    for key, value in sensors.items():
        if value["is_connected"] is True:
            try:
                curs.execute("ALTER TABLE sensors ADD {} DECIMAL(10,2);"
                .format(value["name"]))
            except:
                pass

    close_database_connection(conn, curs)

    return

def create_settings_table():

    conn, curs = open_database_connection()

    curs.execute("CREATE TABLE IF NOT EXISTS settings "
                "(pk TINYINT(1) UNSIGNED PRIMARY"
                " KEY);")
    try:
        curs.execute("INSERT IGNORE INTO settings (pk) VALUES(1)")
    except:
        pass
    for key, value in sensors.items():
        try:
            curs.execute("ALTER TABLE settings ADD ({} DECIMAL(10,2), "
            "{} DECIMAL(10,2));".format(value["upper_alert_name"],
                                        value["lower_alert_name"]))
            curs.execute("UPDATE IGNORE settings SET {} = {}, {} = {} "
                    "WHERE pk=1;".format(value["upper_alert_name"],
                                        value["upper_alert_value"],
                                        value["lower_alert_name"],
                                        value["lower_alert_value"]))
        except:
            pass

    for key, value in misc_setting.items():
        if key == "to_email":
            try:
                curs.execute("ALTER TABLE settings ADD {} VARCHAR(254);"
                .format(key))
                curs.execute("UPDATE IGNORE settings SET {} = '{}' "
                        "WHERE pk=1;".format(key, value))
            except:
                pass

        elif key == "pause_readings":
            try:
                curs.execute("ALTER TABLE settings ADD {} BOOLEAN;"
                .format(key))
                curs.execute("UPDATE IGNORE settings SET {} = {} "
                        "WHERE pk=1;".format(key, value))
            except:
                pass

        elif key == "offset_percent":
            try:
                curs.execute("ALTER TABLE settings ADD {} DECIMAL(10,2);"
                .format(key))
                curs.execute("UPDATE IGNORE settings SET {} = {} "
                        "WHERE pk=1;".format(key, value))
            except:
                pass

        else:
            try:
                curs.execute("ALTER TABLE settings ADD {} INT(10);"
                .format(key))
                curs.execute("UPDATE IGNORE settings SET {} = {} "
                        "WHERE pk=1;".format(key, value))
            except:
                pass

    close_database_connection(conn, curs)

    return


def remove_unused_sensors():

    conn, curs = open_database_connection()

    for key, value in sensors.items():
        if value["is_connected"] is False:
            try:
                curs.execute("ALTER TABLE sensors DROP {};"
                            .format(value["name"]))
            except:
                pass

    close_database_connection(conn, curs)

    return

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def read_1_wire_temp_raw(temp_num):

        f = open(sensors[temp_num]["ds18b20_file"], 'r')
        lines = f.readlines()
        f.close()

        return lines

# Process the Temp Sensor file for errors and convert to degrees C


def read_1_wire_temp(temp_num):

    lines = read_1_wire_temp_raw(temp_num)

    while lines[0].strip()[-3:] != 'YES':
        sleep(0.2)
        lines = read_1_wire_temp_raw()
    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        # Use line below for Celsius
        temp_curr = float(temp_string) / 1000.0
        #Uncomment line below for Fahrenheit
        #temp_curr = ((float(temp_string) / 1000.0) * (9.0 / 5.0)) + 32

        return temp_curr

# read and log each sensor if it is set to True in the sensors list


def log_sensor_readings(all_curr_readings):

    # Create a timestamp and store all readings on the MySQL database

    conn, curs = open_database_connection()

    curs.execute("INSERT INTO sensors (timestamp) VALUES(now());")
    curs.execute("SELECT MAX(timestamp) FROM sensors")
    last_timestamp = curs.fetchone()
    last_timestamp = last_timestamp[0].strftime('%Y-%m-%d %H:%M:%S')

    for readings in all_curr_readings:
        try:
            curs.execute(("UPDATE sensors SET {} = {} WHERE timestamp = '{}'")
                        .format(readings[0], readings[1], last_timestamp))
        except:
            pass

    close_database_connection(conn, curs)

    return

def get_settings_table_values():

    # Get the current alert limit settings from the database

    conn = MySQLdb.connect(servername, username, password, dbname,
                            cursorclass=MySQLdb.cursors.DictCursor)
    curs = conn.cursor()
    curs.execute("SET sql_notes = 0; ")

    curs.execute("SELECT * FROM settings WHERE pk = 1")
    setting_values = curs.fetchone()

    # divide offset percent by 100 to convert to decimal
    setting_values["offset_percent"] = (setting_values["offset_percent"] / 100)

    close_database_connection(conn, curs)

    return setting_values


def send_email(alert_readings):
    #Generate an email when there is a problem with the water

    # Get the email addresses to send the alert to

    all_settings = get_settings_table_values()

    out_of_limit_sensors = ""

    for k, v in alert_readings:
        out_of_limit_sensors = (out_of_limit_sensors + "\n" + k + "  -  " +
                                str(v) + "\n")

    # Build email and send

    fromaddr = "wmedphone@gmail.com"
    toaddr = all_settings["to_email"]
    alladdr = toaddr.split(",")
    msg = MIMEMultipart()
    msg['From'] = "Serenity Admin"
    msg['To'] = toaddr
    msg['Subject'] = "Serenity-HydroPi Alert"

    body = ("Hi\n\nThe following sensor(s) are indicating that there is a problem that needs your attention:\n{}\nPlease check this by logging into the console.\n").format(out_of_limit_sensors.upper())

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        server.starttls()
        server.login(fromaddr, "Visanoob2019!")
        text = msg.as_string()
        server.sendmail(fromaddr, alladdr, text)
        server.quit()
    except:
        pass
    return


def check_sensor_alert_limits(alert_check):

    # Get all the limit settings for the email alert

    all_settings = get_settings_table_values()

    # The IF statement below checks that the main pump relay is active before
    # checking the sensor alert limits. Comment out this line for 24hr
    # monitoring.

    #if RPi.GPIO.input(main_pump_relay) == 1:

    # check the limits for each sensor to trigger the alert email

    for reading in alert_readings:
        for key, value in sensors.items():
            if reading[0] == value["name"]:
                if  ((reading[1] <
                    all_settings[value["lower_alert_name"]])or
                    (reading[1] >
                    all_settings[value["upper_alert_name"]])):
                    alert_check = True
                else:
                    alert_check = False

    return alert_check


def reset_email_sent_flag_if_alerts_clear(email_sent):

    check = []

    # Get all the limit settings for the alert

    all_settings = get_settings_table_values()

    for reading in alert_readings:
        for key, value in sensors.items():
            if reading[0] == value["name"]:

                if  (reading[1] >
                    (all_settings[value["lower_alert_name"]] *
                    (1 + all_settings["offset_percent"])) and
                    (reading[1] <
                    (all_settings[value["upper_alert_name"]] *
                    (1 - all_settings["offset_percent"])))):
                    check.append("OK")

    # Check if all the sensor readings are now OK, if so reset email_sent flag

    if len(alert_readings) == len(check):
        email_sent = False

    return (email_sent)


def reset_pause_readings():

    # Reset pause flag to restart sensor readings

    conn, curs = open_database_connection()

    curs.execute("UPDATE IGNORE settings SET pause_readings = False "
                 "WHERE pk=1;")

    close_database_connection(conn, curs)

    return

def capture_webcam_photo():
    #capture photo through webcam using pygame: https://stackoverflow.com/questions/11094481/capturing-a-single-image-from-my-webcam-in-java-or-python
    
    datetemp = str(datetime.datetime.now())
    datetemp = datetemp.split(".")
    datefilename = ''.join(e for e in datetemp[0] if e.isalnum())
    datefilename = datefilename[:-2]
    datefilename += ".jpg"

    img = cam.get_image()
    pygame.image.save(img,"/var/www/html/camimages/"+datefilename)

def display_welcome():
    print "   _____                      _ __       " 
    print "  / ___/___  ________  ____  (_) /___  __" 
    print "  \__ \/ _ \/ ___/ _ \/ __ \/ / __/ / / /" 
    print " ___/ /  __/ /  /  __/ / / / / /_/ /_/ / " 
    print "/____/\___/_/   \___/_/ /_/_/\__/\__, /  " 
    print "    __  __          __          /____/ _ " 
    print "   / / / /_  ______/ /________  / __ \(_)" 
    print "  / /_/ / / / / __  / ___/ __ \/ /_/ / / " 
    print " / __  / /_/ / /_/ / /  / /_/ / ____/ /  " 
    print "/_/ /_/\__, /\__,_/_/   \____/_/   /_/   " 
    print "      /____/                             " 
    print "\n"
    print "SHyPi is starting..."
    sleep(3)
    print "All services started!"
    print "\n"
    print "IP address:\n"
    print get_ip()
    print "\n"
    print "Output:\n"

def read_sensors():

    capture_webcam_photo()

    all_curr_readings = []
    alert_readings = []
    ref_temp = 25

    # Get the readings from any 1-Wire temperature sensors

    for key, value in sensors.items():
        if value["is_connected"] is True:
            if value["sensor_type"] == "1_wire_temp":
                try:
                    sensor_reading = (round(float(read_1_wire_temp(key)),
                                 value["accuracy"]))
                except:
                    sensor_reading = 50
                    
                all_curr_readings.append([value["name"], sensor_reading])

                if value["test_for_alert"] is True:
                    alert_readings.append([value["name"], sensor_reading])
                if value["is_ref"] is True:
                    ref_temp = sensor_reading

    # Get the readings from any Atlas Scientific temperature sensors

            if value["sensor_type"] == "atlas_scientific_temp":
                device = atlas_i2c(value["i2c"])
                try:
                    sensor_reading = round(float(device.query("R")),
                                value["accuracy"])
                except:
                    sensor_reading = 50
                    
                all_curr_readings.append([value["name"], sensor_reading])
                if value["test_for_alert"] is True:
                    alert_readings.append([value["name"], sensor_reading])
                if value["is_ref"] is True:
                    ref_temp = sensor_reading
                    
    # Get the readings from any Atlas Scientific Elec Conductivity sensors

            if value["sensor_type"] == "atlas_scientific_ec":
                device = atlas_i2c(value["i2c"])
                # Set reference temperature value on the sensor
                device.query("T," + str(ref_temp))
                try:
                    sensor_reading = (round(((float(device.query("R"))) *
                        value["ppm_multiplier"]), value["accuracy"]))
                except:
                    sensor_reading = 10000
                    
                all_curr_readings.append([value["name"], sensor_reading])
                
                if value["test_for_alert"] is True:
                    alert_readings.append([value["name"], sensor_reading])

    # Get the readings from any other Atlas Scientific sensors

            if value["sensor_type"] == "atlas_scientific":
                device = atlas_i2c(value["i2c"])
                # Set reference temperature value on the sensor
                device.query("T," + str(ref_temp))
                try:
                    sensor_reading = round(float(device.query("R")),
                                value["accuracy"])
                except:
                    if value["name"] == "ph":
                        sensor_reading = 2
                    elif value["name"] == "orp":
                        sensor_reading = 1000
                        
                all_curr_readings.append([value["name"], sensor_reading])
                if value["test_for_alert"] is True:
                    alert_readings.append([value["name"], sensor_reading])

    print all_curr_readings
    log_sensor_readings(all_curr_readings)

    # Alert_Readings will return just the readings from sensors we want tested for the email alert

    return alert_readings


# Configuration Settings

# Define the sensor names, what sensors are connected, the sensor type, the
# atlas scientific sensor I2C addresses and define a primary temperature sensor.
# In the case shown below that would be either "temp_1" or "atlas_sensor_1".
# This is the sensor that is in the liquid that is being sampled and is used
# as a reference by the other sensors. If there are no temperature sensors
# connected a default value of 25C will be applied.
#
# Note: The temperature sensors cannot both be set to "is_ref: True", also
# "temp_1" must always be a DS18B20 type sensor and "atlas_sensor_1" must
# always be an Atlas Scientific type temperature sensor so that the reference
# temperature is always set before the other Atlas Scientific sensors are read.

sensors = OrderedDict([("temp_1", {  # DS18B20 Temperature Sensor
                            "sensor_type": "1_wire_temp",
                            "name": "ds18b20_temp",
                            "is_connected": True,
                            "is_ref": False,
                            "ds18b20_file":
                            "/sys/bus/w1/devices/28-0517c20738ff/w1_slave",
                            "accuracy": 1,
                            "test_for_alert": False,
                            "upper_alert_name": "ds18b20_temp_hi",
                            "upper_alert_value": airtemphigh_value,
                            "lower_alert_name": "ds18b20_temp_low",
                            "lower_alert_value": airtemplow_value}),

                       ("atlas_sensor_2", {  # pH/ORP Atlas Scientific Sensor
                            "sensor_type": "atlas_scientific",
                            "name": "ph",
                            "is_connected": True,
                            "is_ref": False,
                            "i2c": 99,
                            "accuracy": 1,
                            "test_for_alert": True,
                            "upper_alert_name": "ph_hi",
                            "upper_alert_value": phhigh_value,
                            "lower_alert_name": "ph_low",
                            "lower_alert_value": phlow_value})])

# Define other alert settings

misc_setting = {"offset_percent": 2,  # Stop toggling when close to alert value
                "pause_readings": False,
                "email_reset_delay": 120,  # 60x2 = 2 minutes for now
                "read_sensor_delay": 300,  # take a reading every 5 minutes for now
                "pause_reset_delay": 1200,  # 60x20 = 20 minutes for now
                "to_email": email_value}

# Define MySQL database login settings

servername = "localhost"
username = "serenityadmin"
password = "Serenity2019!"
dbname = "hydropi"

loops = 0  # Set starting loops count for timing relay and sensor readings

# Define other settings

# number of seconds between sensor readings
time_between_readings = misc_setting["read_sensor_delay"]
alert_check = False
email_sent = False
email_sent_reset = 0
pause_loops = 0

# camera settings
pygame.camera.init()
pygame.camera.list_cameras()
cam = pygame.camera.Camera("/dev/video0",(720,720))
cam.start()

#################
#               #
# Main Program  #
#               #
#################

# Display welcome message

display_welcome()

# Sanity Checks

check_for_only_one_reference_temperature()

# Build/Remove MySQL Database Entries

create_database()
create_sensors_table()
create_settings_table()
remove_unused_sensors()

while True:  # Repeat the code indefinitely
    # Check if sensor readings have been paused, if not then read and store
    # sensor values and check against alert values, send an email if required

    if loops == time_between_readings:
        loops = 0

        # Read delay values from settings table

        delays = get_settings_table_values()
        time_between_readings = delays["read_sensor_delay"]
        email_reset_loop = (delays["email_reset_delay"] //
                                    time_between_readings)
        pause_reset_loop = (delays["pause_reset_delay"] //
                                    time_between_readings)

        if delays["pause_readings"] == 0:
            alert_readings = read_sensors()

            if alert_check is True and email_sent is True:
                email_sent = reset_email_sent_flag_if_alerts_clear(email_sent)
                if email_sent is False:
                    alert_check is False
                    email_sent_reset = 0

            elif alert_check is False:
                alert_check = check_sensor_alert_limits(alert_check)
                if alert_check is True:
                    email_sent = send_email(alert_readings)
                    email_sent = True
                    email_sent_reset = 0

        elif delays["pause_readings"] == 1:
            pause_loops += 1
            if pause_loops == pause_reset_loop:
                reset_pause_readings()
                pause_loops = 0

        if email_sent is True:
            email_sent_reset += 1
            if email_sent_reset == email_reset_loop:
                alert_check = False
                email_sent_reset = 0

    loops += 1
    sleep(1)
