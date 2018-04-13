from datetime import datetime
import time
import json
import requests
from configparser import ConfigParser
import picamera
import os


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
uid = config.get('RaspberryPi', 'uid')
url = config.get('Flask', 'url')

# Define an image filename with the device id and a timestamp
filename = "/home/pi/plant_monitor_rpi/images/{}_{}.jpg".format(\
        uid, datetime.utcnow().strftime("%Y%m%d%H%M%S"))

# Take photo
camera = picamera.PiCamera()
camera.capture(filename)

# Upload to server
files = {'file': (os.path.basename(filename), open(filename, 'rb'), 'image/jpg')}
requests.post(url + "/image", files=files)
