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

while True:

    try:

        volts = float(get_voltage(analog_in ))

        print((volts,))

        time.sleep(1)

    except Exception as e:
        print("error: "+str(e))

        