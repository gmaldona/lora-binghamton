/*
 * CS 526 Internet of Things
 * 
 * Analysis of LoRa/LoRaWAN Under Varied Environmental Conditions 
 * within the Southern Tier Region of New York State
 *
 * contributors: Annie Wu, Callisto Hess, Gregory Maldonado
 * date: 2024-11-15
 *
 * Thomas J. Watson College of Engineering and Applied Sciences, Binghamton University
 */


// -----> TODO TODO TODO replace timer send with a button press send TODO TODO TODO <------

#include <Arduino.h>

#include "LoRaWan_APP.h"

bool overTheAirActivation = true;

uint8_t devEui[] = {LoRaWAN_devEui};
uint8_t appEui[] = {LoRaWAN_appEui};  // you should set whatever your TTN generates. TTN calls this the joinEUI, they are the same thing.
uint8_t appKey[] = {LoRaWAN_appKey};  // you should set whatever your TTN generates

// These are only used for ABP, for OTAA, these values are generated on the Nwk Server, you should not have to change these values
uint8_t nwkSKey[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
uint8_t appSKey[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
uint32_t devAddr = (uint32_t)0x00000000;

/*LoraWan channelsmask*/
uint16_t userChannelsMask[6] = {0xFF00, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000};

/*LoraWan region, select in arduino IDE tools*/
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;  // we define this as a user flag in the .ini file.

/*LoraWan Class, Class A and Class C are supported*/
DeviceClass_t loraWanClass = CLASS_A;

/*the application data transmission duty cycle.  value in [ms].*/
uint32_t appTxDutyCycle = 15000;

static const uint8_t PREAMBLE_SIZE = 4;

/*ADR enable*/
bool loraWanAdr = true;

// uint32_t license[4] = {};

/* Indicates if the node is sending confirmed or unconfirmed messages */
bool isTxConfirmed = true;

/* Application port */
uint8_t appPort = 1;
/*!
 * Number of trials to transmit the frame, if the LoRaMAC layer did not
 * receive an acknowledgment. The MAC performs a datarate adaptation,
 * according to the LoRaWAN Specification V1.0.2, chapter 18.4, according
 * to the following table:
 *
 * Transmission nb | Data Rate
 * ----------------|-----------
 * 1 (first)       | DR
 * 2               | DR
 * 3               | max(DR-1,0)
 * 4               | max(DR-1,0)
 * 5               | max(DR-2,0)
 * 6               | max(DR-2,0)
 * 7               | max(DR-3,0)
 * 8               | max(DR-3,0)
 *
 * Note, that if NbTrials is set to 1 or 2, the MAC will not decrease
 * the datarate, in case the LoRaMAC layer did not receive an acknowledgment
 */
uint8_t confirmedNbTrials = 8;

/* Prepares the payload of the frame */
static void prepareTxFrame(uint8_t port) {
    /*appData size is LORAWAN_APP_DATA_MAX_SIZE which is defined in "commissioning.h".
     *appDataSize max value is LORAWAN_APP_DATA_MAX_SIZE.
     *if enabled AT, don't modify LORAWAN_APP_DATA_MAX_SIZE, it may cause system hanging or failure.
     *if disabled AT, LORAWAN_APP_DATA_MAX_SIZE can be modified, the max value is reference to lorawan region and SF.
     *for example, if use REGION_CN470,
     *the max value for different DR can be found in MaxPayloadOfDatarateCN470 refer to DataratesCN470 and BandwidthsCN470 in "RegionCN470.h".
     */
    // This data can be changed, just make sure to change the datasize as well.

    /*
        // clang-format off

               Packet Structure
         +------------+--------------+
         |  PREAMBLE  |     DATA     |
         +------------+--------------+
            4 bytes        N bytes

        // clang-format on
    */

    // PACKET PREAMBLE - AGC1

    appData[0] = 0x41;  // A
    appData[1] = 0x43;  // C
    appData[2] = 0x47;  // G
    appData[3] = 0x31;  // 1

    // https://stackoverflow.com/questions/62903255/converting-hex-to-float
    union {
        double _double;
        uint64_t _int;
    } U_double;

    uint8_t index = PREAMBLE_SIZE; 
    // gps coordinate of Binghamton University
    const double gps_coordinate[2] = {42.08950838980908, -75.96947777439027};

    for (uint8_t i = 0; i < 2; ++i) {
        U_double._double = gps_coordinate[i];
        // top most bit shift v           v lower most bit shift
        for (int8_t shift = 56; shift >= 0; shift -= 8) {
            appData[index] = (uint8_t)(U_double._int >> shift) & 0xFF;
            index++;
        }
    }

    appDataSize = PREAMBLE_SIZE + (sizeof(double) * 2);
}

RTC_DATA_ATTR bool firstrun = true;

void setup() {
    Serial.begin(115200);
    Mcu.begin();
    if (firstrun) {
        LoRaWAN.displayMcuInit();
        firstrun = false;
    }
    deviceState = DEVICE_STATE_INIT;
}

void loop() {
    switch (deviceState) {
        case DEVICE_STATE_INIT: {
#if (LORAWAN_DEVEUI_AUTO)
            LoRaWAN.generateDeveuiByChipID();
#endif
            LoRaWAN.init(loraWanClass, loraWanRegion);
            break;
        }
        case DEVICE_STATE_JOIN: {
            LoRaWAN.displayJoining();
            LoRaWAN.join();
            if (deviceState == DEVICE_STATE_SEND) {
                LoRaWAN.displayJoined();
            }
            break;
        }
        case DEVICE_STATE_SEND: {
            LoRaWAN.displaySending();
            prepareTxFrame(appPort);
            LoRaWAN.send();
            deviceState = DEVICE_STATE_CYCLE;
            break;
        }
        case DEVICE_STATE_CYCLE: {
            // Schedule next packet transmission
            txDutyCycleTime = appTxDutyCycle + randr(0, APP_TX_DUTYCYCLE_RND);
            LoRaWAN.cycle(txDutyCycleTime);
            deviceState = DEVICE_STATE_SLEEP;
            break;
        }
        case DEVICE_STATE_SLEEP: {
            LoRaWAN.displayAck();
            LoRaWAN.sleep(loraWanClass);
            break;
        }
        default: {
            deviceState = DEVICE_STATE_INIT;
            break;
        }
    }
}