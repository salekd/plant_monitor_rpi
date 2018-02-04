# Make sure python can see the miflora module
import sys
sys.path.append("/home/pi/miflora")

from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from datetime import datetime
import time
import json
import requests
from configparser import ConfigParser
import picamera
from twython import Twython


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
consumer_key = config.get('Twitter', 'consumer_key')
consumer_secret = config.get('Twitter', 'consumer_secret')
access_key = config.get('Twitter', 'access_key')
access_secret = config.get('Twitter', 'access_secret')

# Take measurement
poller = MiFloraPoller(mac, BluepyBackend)
poller.fill_cache()
measurement = poller._parse_data()

# Define an image filename with the device id and a timestamp
filename = "/home/pi/plant_monitor_rpi/images/{}_{}.jpg".format(\
        mac.replace(':', ''), datetime.utcnow().strftime("%Y%m%d%H%M%S"))

# Take photo
camera = picamera.PiCamera()
camera.capture(filename)

# Send twitter message
message = "The measurements from device {} are: moisture={}, temperature={}, conductivity={}, light={}".format(\
        mac, measurement["moisture"], measurement["temperature"], measurement["conductivity"], measurement["light"])
photo = open(filename, 'rb')
twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
response = twitter.upload_media(media=photo)
twitter.update_status(status=message, media_ids=[response['media_id']])
