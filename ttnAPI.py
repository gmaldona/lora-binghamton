import paho.mqtt.client as mqtt
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


# Set up MQTT client
client = mqtt.Client()
client.username_pw_set("cs-426-526-iot@ttn", "NNSXS.ZGF7PM26FZCMYUMK6WB3XQEV7ZLHCKJAISKXFNY.N7JWNKHQDSMU5NLNX4ISGJO4ECAW32SF6RVCNJX3EBUBISKXXY3A")  # Replace with your password
client.on_connect = on_connect
client.on_message = on_message

# Connect to TTN MQTT broker
client.connect("nam1.cloud.thethings.network", 1883, 60)
client.loop_forever()
