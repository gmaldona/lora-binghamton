#!/usr/bin/env python

# CS 526 Internet of Things
# 
# Analysis of LoRa/LoRaWAN Under Varied Environmental Conditions 
# within the Southern Tier Region of New York State
#
# contributors: Annie Wu, Callisto Hess, Gregory Maldonado
# date: 2024-11-15
#
# Thomas J. Watson College of Engineering and Applied Sciences, Binghamton University

import base64
import configparser
from datetime import datetime
import json
import decoder as agc_decode

import paho.mqtt.client as mqtt

## ========== Code reference from lab 4 post lab ========== 

decoder = agc_decode.decode

# Callback when successfully connected to MQTT broker.
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker.")

    if rc != 0:
        print(" Error, result code: {}".format(rc))


# Callback function to handle incoming MQTT messages
def on_message(client, userdata, message):
    global decoder
    
    # Timestamp on reception.
    current_date = datetime.now()

    # Handle TTN packet format.
    message_str = message.payload.decode("utf-8")
    message_json = json.loads(message_str)
    encoded_payload = message_json["uplink_message"]["frm_payload"]
    raw_payload = base64.b64decode(encoded_payload)

    if len(raw_payload) == 0:
        # Nothing we can do with an empty payload.
        return
    
    preamble = raw_payload[:4]
    remaining_payload = raw_payload[4:]

    if str(preamble) == 'agc1':
        try:
            message = decoder(remaining_payload)
        except Exception as e:
            print(e)
            print("payload: {}".format(remaining_payload))
            return

        if message:
            print(f'[{current_date}] {message}')


def main():
    # Read in config file with MQTT details.
    config = configparser.ConfigParser()
    config.read("config.ini")

    # MQTT broker details
    broker_address = config["mqtt"]["broker"]
    username = config["mqtt"]["username"]
    password = config["mqtt"]["password"]

    topic = "v3/+/devices/+/up"

    # MQTT client setup
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    # Setup callbacks.
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker.
    client.username_pw_set(username, password)
    client.tls_set()
    client.connect(broker_address, 8883)

    # Subscribe to the MQTT topic and start the MQTT client loop
    client.subscribe(topic)
    client.loop_forever()

if __name__ == '__main__':
    main()