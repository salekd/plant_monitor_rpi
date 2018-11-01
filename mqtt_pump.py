import paho.mqtt.client as mqtt
import ssl
import logging
import pathlib
from time import sleep
import RPi.GPIO as GPIO


def on_connect(mqttc, obj, flags, rc):
    logger.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe("salekd/pump", qos=0)


def on_disconnect(mqttc, obj, rc):
    if rc != 0:
        logger.warning("Unexpected disconnection.")


def on_message(mqttc, obj, msg):
    logger.info("Received message '" + str(msg.payload) + "' on topic '" + msg.topic + "' with QoS " + str(msg.qos))
    pump_gpio = 18
    pump_time = int(msg.payload)
    logger.info("Pumping water for {} s.".format(pump_time))
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pump_gpio, GPIO.OUT, initial=GPIO.HIGH)
    sleep(pump_time)
    GPIO.output(pump_gpio, GPIO.LOW)
    GPIO.cleanup()


def on_publish(mqttc, obj, mid):
    logger.info("Messaged ID: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    logger.info("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    logger.log(level, string)


mqttc = mqtt.Client()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
mqttc.enable_logger(logger)

mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.username_pw_set("sub_client", "ion-adept-hoc-hood")
parent_dir = pathlib.Path(__file__).parent.resolve()
mqttc.tls_set(str(parent_dir/ ".." / "ca.crt"), tls_version=ssl.PROTOCOL_TLSv1_2)
mqttc.connect("mosquitto.projects.sda.surfsara.nl", 50103, 60)

mqttc.loop_forever()
