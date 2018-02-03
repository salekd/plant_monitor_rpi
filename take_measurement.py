# Make sure python can see the miflora module
import sys
sys.path.append("/home/pi/miflora")

from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from datetime import datetime
import time
import json
import requests
from collections import OrderedDict
from configparser import ConfigParser


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
url = config.get('Flask', 'url')

# Take measurement
poller = MiFloraPoller(mac, BluepyBackend)
poller.fill_cache()
measurement = poller._parse_data()

# Add timestamp
measurement["timestamp"] = str(datetime.utcnow())

# Make sure the entries are in the correct order
keys = ['timestamp', 'moisture', 'temperature', 'conductivity', 'light']
ordered = OrderedDict([(key, measurement[key]) for key in keys])

print(json.dumps(ordered))

# Append to a csv file for the device
csvfile = "/home/pi/plant_monitor/measurements/{}.csv".format(mac.replace(':', ''))
with open(csvfile, "a") as f:
    f.write(", ".join([str(x) for x in ordered.values()]) + '\n')

# Add device id
measurement["device"] = mac

# Upload to server
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(url + "/measurement", data=json.dumps(measurement), headers=headers)
