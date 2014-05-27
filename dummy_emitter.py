#!/usr/bin/env python

import paho.mqtt.client as paho
import sys
import time
from random import randrange
import click


@click.command()
@click.option('--broker', default="localhost", help='MQTT Broker host')
@click.option('--port', default=1883, help='MQTT Broker port')
@click.option('--topic', default="1/1", help='MQTT topic to publish')
@click.option('--debug', is_flag=True)
def main(broker, port, topic, debug):
    """Generate dummy sensor data and publish to MQTT broker on localhost"""
    mqttc = paho.Client()
    mqttc.connect(broker, port, 60)

    while True:
        randnum = randrange(15, 30)
        mqttc.publish(topic, randnum)
        if debug:
            print("Published %s %d" % (topic, randnum))
        time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
