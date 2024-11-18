#!/usr/bin/env python

# CS 526 Internet of Things
# 
# Analysis of LoRa/LoRaWAN Under Varied Environmental Conditions 
# within the Southern Tier Region of New York State
#
# contributors: Annie Wu, Callisto Hess, Gregory Maldonado
# date: 2024-07-04
#
# Thomas J. Watson College of Engineering and Applied Sciences, Binghamton University

import struct

def decode(payload):
    # The first 8 bytes are the lat coordinates
    # The last 8 bytes are the long coordinates 
    lat  = struct.unpack('>d', payload[0:8])[0]
    long = struct.unpack('>d', payload[8:16])[0]

    return (lat, long)
