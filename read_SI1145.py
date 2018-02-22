from SI1145.SI1145 import SI1145
from datetime import datetime
import time
import json
import requests
from configparser import ConfigParser


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
uid = config.get('RaspberryPi', 'uid')
url = config.get('Flask', 'url')

# Take measurement
sensor = SI1145()
measurement = {}
measurement["visible"] = sensor.readVisible()
measurement["IR"] = sensor.readIR()
measurement["UV"] = sensor.readUV()
print(measurement)

# Add timestamp
measurement["timestamp"] = str(datetime.utcnow())

# Add device id
measurement["device"] = "SI1145_{}".format(uid)

# Append to a csv file for the device
csvfile = "/home/pi/plant_monitor_rpi/measurements/{}.csv".format(measurement["device"])
with open(csvfile, "a") as f:
    # Make sure the entries are in the correct order
    f.write("{}, {}, {}, {}\n".format(measurement["timestamp"],
        measurement["visible"], measurement["IR"], measurement["UV"]))

# Upload to server
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(url + "/si1145", data=json.dumps(measurement), headers=headers)
