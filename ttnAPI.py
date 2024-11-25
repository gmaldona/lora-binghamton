import paho.mqtt.client as mqtt
import configparser
import os
from pathlib import Path
import json
import csv
from datetime import datetime, timedelta
import re

# MQTT callback for when connected to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code", rc)
    # Subscribe to the uplink topic
    client.subscribe("v3/cs-426-526-iot@ttn/devices/+/up")

# MQTT callback for incoming messages
def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    
    # Extract metadata and timestamps
    uplink_message = payload.get("uplink_message", {})
    metadata_list = uplink_message.get("rx_metadata", [])
    received_at = uplink_message.get("received_at", "N/A")  # TTN's timestamp
    
    # Open CSV file to save data
    with open("lorawan_data_with_time.csv", mode="a") as file:
        writer = csv.writer(file)
        
        # Iterate through all metadata (in case of multiple gateways)
        for metadata in metadata_list:
            rssi = metadata.get("rssi", "N/A")
            snr = metadata.get("snr", "N/A")
            spreading_factor = uplink_message.get("settings", {}).get("data_rate", {}).get("lora", {}).get("spreading_factor", "N/A")
            frequency = uplink_message.get("settings", {}).get("frequency", "N/A")
            airtime = uplink_message.get("consumed_airtime", "N/A")
            received_time = metadata.get("received_at", uplink_message.get("received_at", "N/A"))  # Prefer rx_metadata timestamp if available
            timestamp = uplink_message.get("settings", {}).get("timestamp", "N/A")

            # Formatting Data
            received_time = re.sub(r"(\.\d{6})\d*", r"\1", received_time)
            parsed_time = datetime.strptime(received_time, "%Y-%m-%dT%H:%M:%S.%fZ")- timedelta(hours=5)
            formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
            # Write to the CSV file
            writer.writerow([formatted_time, timestamp, rssi, snr, spreading_factor, frequency, airtime])


def main():
    os.makedirs('logs', exist_ok=True)
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
