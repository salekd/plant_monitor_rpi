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
temperature, pressure, humidity = bme280.readBME280All()
measurement = {}
measurement["temperature"] = temperature
measurement["pressure"] = round(pressure, 2)
measurement["humidity"] = round(humidity, 2)
print(measurement)

# Add timestamp
measurement["timestamp"] = str(datetime.utcnow())

#Add device id
measurement["device"] = "BME280_{}".format(uid)

# Append to a csv file for the device
csvfile = "/home/pi/plant_monitor_rpi/measurements/{}.csv".format(measurement["device"])
with open(csvfile, "a") as f:
    # Make sure the entries are in the correct order
    f.write("{}, {}, {}, {}\n".format(measurement["timestamp"],
        measurement["temperature"], measurement["pressure"], measurement["humidity"]))

# Upload to server
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(url + "/bme280", data=json.dumps(measurement), headers=headers)
