from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from datetime import datetime
import time
import json
import requests
from configparser import ConfigParser
import paho.mqtt.publish as publish
import pathlib
import ssl


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
url = config.get('Flask', 'url')
hostname = config.get('MQTT', 'hostname')
topic = config.get('MQTT', 'topic')

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
#headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
#requests.post(url + "/measurement", data=json.dumps(measurement), headers=headers)

# Send to test.mosquitto.org
#publish.single(topic, payload=json.dumps(measurement), hostname=hostname)
#publish.single(topic, payload=json.dumps(measurement), hostname="145.100.41.54", port=50103)
#publish.single(topic, payload=json.dumps(measurement), hostname="mosquitto.projects.sda.surfsara.nl", port=50103)
#publish.single(topic, payload=json.dumps(measurement), hostname="mosquitto.projects.sda.surfsara.nl", port=50103)
auth = {"username": "pub_client", "password": "igloo-mardi-ira-aye"}
parent_dir = pathlib.Path(__file__).parent.resolve()
tls = {"ca_certs": str(parent_dir / ".." / "ca.crt"), "tls_version": ssl.PROTOCOL_TLSv1_2}
publish.single(topic, payload=json.dumps(measurement), hostname="mosquitto.projects.sda.surfsara.nl", port=50103, auth=auth, tls=tls)
