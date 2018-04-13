from time import sleep
import RPi.GPIO as GPIO
from miflora.miflora_poller import MiFloraPoller
from miflora.backends.bluepy import BluepyBackend
from configparser import ConfigParser


# Read config file
config = ConfigParser()
config.read('raspberrypi.cfg')
mac = config.get('MiFlora', 'mac')
moisture_threshold = config.getint('Pump', 'moisture_threshold')
pump_time = config.getint('Pump', 'pump_time')
pump_gpio = config.getint('Pump', 'pump_gpio')

# Take measurement
poller = MiFloraPoller(mac, BluepyBackend)
poller.fill_cache()
measurement = poller._parse_data()
print(measurement)

if measurement['moisture'] < moisture_threshold:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pump_gpio, GPIO.OUT, initial=GPIO.HIGH)
    sleep(pump_time)
    GPIO.output(pump_gpio, GPIO.LOW)
    GPIO.cleanup()
