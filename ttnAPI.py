import paho.mqtt.client as mqtt
import configparser
import os
from pathlib import Path
import json
import csv

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
            gateway_time = metadata.get("time", received_at)  # Use gateway time if available
            
            # Print and write to CSV
            print(f"Time: {gateway_time}, RSSI: {rssi}, SNR: {snr}")
            writer.writerow([gateway_time, rssi, snr])


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
