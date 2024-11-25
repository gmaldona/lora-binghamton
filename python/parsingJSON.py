import json
import csv

# Load the JSON file
with open("../data/acg-iot-3_live_data_1732482931779.json", "r") as file:  # Replace with your actual filename
    data = json.load(file)

print(f"Type of Data: {type(data)}")  # Confirming the data type is a list

# Open a CSV file to write the extracted data
with open("../data/lorawan_extracted_data.csv", "w", newline="") as csvfile:
    # Define CSV writer and header
    writer = csv.writer(csvfile)
    writer.writerow(["Received Time", "Timestamp", "RSSI", "SNR", "SF", "Frequency", "Airtime"])

    # Iterate over each item in the list
    for record in data:
        uplink_message = record.get("data", {}).get("uplink_message", {})
        rx_metadata_list = uplink_message.get("rx_metadata", [])

        for rx_metadata in rx_metadata_list:
            # Extract required fields
            rssi = rx_metadata.get("rssi", "N/A")
            snr = rx_metadata.get("snr", "N/A")
            spreading_factor = uplink_message.get("settings", {}).get("data_rate", {}).get("lora", {}).get("spreading_factor", "N/A")
            frequency = uplink_message.get("settings", {}).get("frequency", "N/A")
            airtime = uplink_message.get("consumed_airtime", "N/A")
            received_time = rx_metadata.get("received_at", uplink_message.get("received_at", "N/A"))  # Prefer rx_metadata timestamp if available
            timestamp = uplink_message.get("settings", {}).get("timestamp", "N/A")

            # Write to the CSV file
            writer.writerow([received_time, timestamp, rssi, snr, spreading_factor, frequency, airtime])

print("Data extraction completed! Check 'lorawan_extracted_data.csv'.")
