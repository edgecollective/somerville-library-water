import board
import busio
import digitalio
from digitalio import DigitalInOut
import time
import gc

from analogio import AnalogIn


def get_voltage(pin):
    return (pin.value * 3.3) / 65536

analog_in = AnalogIn(board.A0)

# Get Wifi and FarmOS details
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

WIFI_ESSID=secrets['ssid']
WIFI_PASS=secrets['password']
farmos_pubkey=secrets['farmos_pubkey']
farmos_privkey=secrets['farmos_privkey']

base_url= "https://edgecollective.farmos.net/farm/sensor/listener/"

JSON_POST_URL = base_url+farmos_pubkey+"?private_key="+farmos_privkey

# esp32

import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests as requests

esp32_cs = DigitalInOut(board.D10)
esp32_ready = DigitalInOut(board.D9)
esp32_reset = DigitalInOut(board.D11)

esp_spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(esp_spi, esp32_cs, esp32_ready, esp32_reset)


def connect(essid,password): # note that these are arguments are b'essid' and b'password'
    print("Connecting to AP...")
    while not esp.is_connected:
        try:
            esp.connect_AP(essid, password)
        except RuntimeError as e:
            print("could not connect to AP, retrying: ",e)
            continue
    print("Connected to", str(esp.ssid, 'utf-8'), "\tRSSI:", esp.rssi)

    # Initialize a requests object with a socket and esp32spi interface
    requests.set_socket(socket, esp)

# main loop

while True:


    try:

        volts = 2*float(get_voltage(analog_in ))

        volts = 0.0

        json_data = {"volts" : volts}

        print("Posting to ",JSON_POST_URL)

        connect(WIFI_ESSID,WIFI_PASS)

        response = requests.post(JSON_POST_URL, json=json_data)
        print(response.content)

        response.close()

        print("Done. Sleeping ... ")
        time.sleep(90)
            
        except Exception as e:
            print("error: "+str(e))

        