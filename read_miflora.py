from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from datetime import datetime
import time
import json
import requests
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
print(measurement)

# Add timestamp
measurement["timestamp"] = str(datetime.utcnow())

# Append to a csv file for the device
csvfile = "/home/pi/plant_monitor_rpi/measurements/{}.csv".format(mac.replace(':', ''))
with open(csvfile, "a") as f:
    # Make sure the entries are in the correct order
    f.write("{}, {}, {}, {}, {}\n".format(measurement["timestamp"],
        measurement["moisture"], measurement["temperature"], measurement["conductivity"], measurement["light"]))

# Add device id
measurement["device"] = mac

# Upload to server
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
requests.post(url + "/measurement", data=json.dumps(measurement), headers=headers)
