from time import sleep
import RPi.GPIO as GPIO
from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from configparser import ConfigParser
import logging
import sys
from datetime import datetime
import time
import json
import requests


# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handler
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(logging.INFO)

# Specify the logging format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
url = config.get('Flask', 'url')
moisture_threshold = config.getint('Pump', 'moisture_threshold')
pump_time = config.getint('Pump', 'pump_time')
pump_gpio = config.getint('Pump', 'pump_gpio')
logger.info("Moisture threshold = {}".format(moisture_threshold))

# Take measurement
poller = MiFloraPoller(mac, BluepyBackend)
poller.fill_cache()
measurement = poller._parse_data()
logger.info("moisture = {}, temperature = {}, conductivity = {}, light = {}".format(
    measurement["moisture"], measurement["temperature"],
    measurement["conductivity"], measurement["light"]))

if measurement['moisture'] < moisture_threshold:
    logger.info("Pumping water for {} s.".format(pump_time))
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pump_gpio, GPIO.OUT, initial=GPIO.HIGH)
    sleep(pump_time)
    GPIO.output(pump_gpio, GPIO.LOW)
    GPIO.cleanup()

    pump_log = {}
    pump_log["timestamp"] = str(datetime.utcnow())
    pump_log["device"] = mac
    pump_log["duration"] = pump_time

    # Append to a csv file for the device
    csvfile = "/home/pi/plant_monitor_rpi/measurements/pump_{}.csv".format(mac.replace(':', ''))
    with open(csvfile, "a") as f:
        # Make sure the entries are in the correct order
        f.write("{}, {}\n".format(pump_log["timestamp"], pump_log["duration"]))

    # Upload to server
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    requests.post(url + "/pump", data=json.dumps(pump_log), headers=headers)
