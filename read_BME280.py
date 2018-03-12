import smbus2
import bme280
from datetime import datetime
import json
import requests
from configparser import ConfigParser


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
uid = config.get('RaspberryPi', 'uid')
url = config.get('Flask', 'url')

# Take measurement
port = 1
address = 0x76
bus = smbus2.SMBus(port)
bme280.load_calibration_params(bus, address)
data = bme280.sample(bus, address)
print(data)

measurement = {}
measurement["temperature"] = round(data.temperature, 2)
measurement["pressure"] = round(data.pressure, 2)
measurement["humidity"] = round(data.humidity, 2)
print(measurement)

# Add timestamp
measurement["timestamp"] = str(datetime.utcnow())

# Add device id
measurement["device"] = uid

# Append to a csv file for the device
csvfile = "/home/pi/plant_monitor_rpi/measurements/BME280_{}.csv".format(measurement["device"])
with open(csvfile, "a") as f:
    # Make sure the entries are in the correct order
    f.write("{}, {}, {}, {}\n".format(measurement["timestamp"],
        measurement["temperature"], measurement["pressure"], measurement["humidity"]))

# Upload to server
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(url + "/bme280", data=json.dumps(measurement), headers=headers)
