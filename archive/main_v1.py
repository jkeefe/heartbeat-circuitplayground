# SPDX-FileCopyrightText: 2022 Isaac Wellish for Adafruit Industries
#
# SPDX-License-Identifier: MIT

## v1 ... Works! 
#       - External LED on D13
#       - Nice fade on External LED
#       - Neopixels on face show heart rate in 10s (1 = 50bpm, 2 = 60bp, 3 = 70 bpm etc)

"""
SPDX-FileCopyrightText: 2022 Isaac Wellish for Adafruit Industries
SPDX-License-Identifier: MIT
Circuit Playground Bluefruit BLE Heart Rate Display
Read heart rate data from a heart rate peripheral using
the standard BLE heart rate service.
The heart rate monitor connects to the CPB via BLE.
LEDs on CPB blink to the heart rate of the user.
"""

import time
import board
import neopixel
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble_heart_rate import HeartRateService
from digitalio import DigitalInOut, Direction, Pull
import pwmio

#on-board status LED setup
red_led = DigitalInOut(board.D13)
red_led.direction = Direction.OUTPUT
red_led.value = True

strand = pwmio.PWMOut(board.AUDIO)

# # set up button using board module
# button = DigitalInOut(board.BUTTON_A)
# button.direction = Direction.INPUT
# button.pull = Pull.DOWN
## use if button.value: ..

use_neos = False


#NeoPixel code
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=False)
RED = (255, 0, 0)
LIGHTRED = (25, 0, 0)
BLANK = (0,0,0)

def color_chase(color, wait):
    for i in range(10):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(1)

    if not use_neos:
        pixels.fill(BLANK)
        pixels.show()

def scale_a(value):
    # Scale a value from 0-65535 (AnalogIn range) to 0-255 (RGB range)
    return int(value / 65535 * 255)

def scale_b(value):
    # Scale a value from 0-255 (RGB range) to 0-65535 (AnalogOut range) 
    return int(value * 65535 / 255)



# animation to show initialization of program
color_chase(RED, 0.1)  # Increase the number to slow down the color chase

#starting bpm value
bpm = 60

# PyLint can't find BLERadio for some reason so special case it here.
ble = adafruit_ble.BLERadio()    # pylint: disable=no-member

hr_connection = None

# Start with a fresh connection.
if ble.connected:
    time.sleep(1)

    for connection in ble.connections:
        if HeartRateService in connection:
            connection.disconnect()
        break

while True:
    print("Scanning...")
    red_led.value = True
    time.sleep(1)

    for adv in ble.start_scan(ProvideServicesAdvertisement, timeout=5):

        if HeartRateService in adv.services:
            print("found a HeartRateService advertisement")
            hr_connection = ble.connect(adv)
            time.sleep(2)
            print("Connected")
            red_led.value = False
            break

    # Stop scanning whether or not we are connected.
    ble.stop_scan()
    print("Stopped scan")
    red_led.value = False
    time.sleep(0.5)

    # may want to look for my specific device here and bail if not correct ... JK TODO
    if hr_connection and hr_connection.connected:
        print("Fetch connection")
        if DeviceInfoService in hr_connection:
            dis = hr_connection[DeviceInfoService]
            try:
                manufacturer = dis.manufacturer
            except AttributeError:
                manufacturer = "(Manufacturer Not specified)"
            try:
                model_number = dis.model_number
            except AttributeError:
                model_number = "(Model number not specified)"
            print("Device:", manufacturer, model_number)
        else:
            print("No device information")
        hr_service = hr_connection[HeartRateService]
        print("Location:", hr_service.location)

        while hr_connection.connected:
            values = hr_service.measurement_values
            # print(values)  # returns the full heart_rate data set
            if values:
                bpm = (values.heart_rate)
                if values.heart_rate == 0:
                    print("-")
                else:
                    time.sleep(0.1)

            if bpm != 0: # prevent from divide by zero
                #find interval time between beats
                bps = bpm / 60
                period = 1 / bps
                time_on = 0.375 * period
                time_off = period - time_on 

            #     # Blink leds at the given BPM
            #     pixels.fill(RED)
            #     pixels.show()
            #     time.sleep(time_on)
            #     pixels.fill(LIGHTRED)
            #     pixels.show()
            #     time.sleep(time_off)

                # Fade up and down in a given period

                # # good for on-board neopixels
                # animation_steps = 40
                # brightest = 200
                # dimmest = 90

                # # good for LEDS
                animation_steps = 40
                brightest = 255
                dimmest = 40

                animation_step_length = period / animation_steps
                brightness_difference_per_period = int( (brightest - dimmest) / (animation_steps) )

                ## Could set brightest based on range of bpm, too
                ## Dimmest too, for that matter

                print(bpm, period, animation_step_length)

                # get dim
                for illumination in range( brightest, dimmest, -brightness_difference_per_period):
                    # neopixels on board
                    COLOR = (illumination, 0, 0)

                    if use_neos:
                        pixels.fill(COLOR)
                        pixels.show()
                    else:
                        monitor_arc = int(bpm/10) -5
                        for i in range(0, 10):
                            if i <= monitor_arc:
                                pixels[i] = LIGHTRED
                            else:
                                pixels[i] = BLANK
                        pixels.show()

                    # external LED
                    strand.duty_cycle = scale_b(illumination)

                    time.sleep(animation_step_length)

                    

