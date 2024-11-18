# IoT TTN Receiver

This Python app connects to the TTN MQTT broker and subscribes to all messages
from the class TTN app. It then parses the first set of byte and dispatches to the decoder.

## Expected Packet Format

| Preamble (4 bytes) | latitude coordinate (8 bytes) | longitude coordinate (8 bytes) |
|--------------------|-------------------------------|--------------------------------|

Preamble is `ACG1` and for testing purposes the GPS coordinates that are being sent are 
the coordinates of Binghamton University `(42.08950838980908, -75.96947777439027)`.
