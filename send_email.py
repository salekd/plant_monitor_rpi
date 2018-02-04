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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
user = config.get('Email', 'user')
pwd = config.get('Email', 'pwd')


# Take measurement
poller = MiFloraPoller(mac, BluepyBackend)
poller.fill_cache()
measurement = poller._parse_data()

# Define an image filename with the device id and a timestamp
filename = "/home/pi/plant_monitor/images/{}_{}.jpg".format(\
        mac.replace(':', ''), datetime.utcnow().strftime("%Y%m%d%H%M%S"))

# Take photo
camera = picamera.PiCamera()
camera.capture(filename)

# Send e-mail
msgRoot = MIMEMultipart()
msgRoot["From"] = user
msgRoot["To"] = user
msgRoot["Subject"] = "Plant monitor"

message = "The measurements from device {} are: moisture={}, temperature={}, conductivity={}, light={}".format(\
        mac, measurement["moisture"], measurement["temperature"], measurement["conductivity"], measurement["light"])
msgText = MIMEText(message)
msgRoot.attach(msgText)

photo = open(filename, 'rb')
msgImg = MIMEImage(photo.read(), 'jpeg')
msgImg.add_header("Content-Disposition", "attachment", filename=os.path.basename(filename))
msgRoot.attach(msgImg)

try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(user, pwd)
    server.sendmail(msgRoot["From"], msgRoot["To"], msgRoot.as_string())
    server.close()
    print("successfully sent the mail")
except:
    print("failed to send mail")
