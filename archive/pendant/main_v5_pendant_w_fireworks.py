# SPDX-FileCopyrightText: 2022 Isaac Wellish for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Modified by John Keefe December 2023 | johnkeefe.net

import time
import board
import neopixel
import adafruit_ble
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_ble_heart_rate import HeartRateService
from digitalio import DigitalInOut, Direction
import random

# marry this to a specific heart-rate monitor
serial_number = ""
my_serial_number = "805439979" # note that it's a string 

# when do the fireworks fly?
fireworks_threshold = 98 # bpm

#on-board status LED setup
red_led = DigitalInOut(board.D13)
red_led.direction = Direction.OUTPUT
red_led.value = True

#NeoPixel code
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.4, auto_write=False)
RED = (255, 0, 0)
LIGHTRED = (25, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 50,50)
LIGHTPINK = (40, 10,10)
WHITE = (255, 255, 255)
SOFTWHITE = (150,150,150)
BLANK = (0,0,0)

def color_chase(color, wait):
    for i in range(10):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(1)

def fill_color(red, green, blue, fade, brightness):
    for i in range(10):
        pixels[i] = (red*fade*brightness, green*fade*brightness, blue*fade*brightness)
    pixels.show()

def fill_color_simple(color):
    for i in range(10):
        pixels[i] = color
    pixels.show()

def fireworks():
    flash_length = 0.05
    seconds = 5
    flashes = int(seconds/flash_length)

    for f in range(flashes):
        fireworks_colors = [RED, PINK, LIGHTPINK, SOFTWHITE, BLANK]
        fireworks_leds = [ [0,1,2], [3,4,5], [6,7,8,9]]
        random_color = random.choice(fireworks_colors)
        random_leds = random.choice(fireworks_leds)

        fill_color_simple(BLANK)

        # picks 3 or 4 around the ring
        for i in random_leds:
            pixels[i] = random_color
        pixels.show()

        time.sleep(flash_length)
    
def make_interpolater(left_min, left_max, right_min, right_max): 
    # Figure out how 'wide' each range is  
    leftSpan = left_max - left_min  
    rightSpan = right_max - right_min  

    # Compute the scale factor between left and right values 
    scaleFactor = float(rightSpan) / float(leftSpan) 

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        if value < left_min:
            value = left_min
        if value > left_max:
            value = left_max
        return right_min + (value-left_min)*scaleFactor

    return interp_fn

    ## usage: 
    ## scaler = make_interpolater(0, 10, 100, 200)
    ## x = scaler(50)
    ## ... can make many in each project!

def dump(obj):
  for attr in dir(obj):
    print("obj.%s = %r" % (attr, getattr(obj, attr)))

# # animation to show initialization of program
# color_chase(LIGHTRED, 0.1)  # Increase the number to slow down the color chase

### -- settings for color and beats --- ###

# make color range
# 50 bpm = 255,130,0 
# 85 bpm = 255,0,0 (full red)
# ... so scale the green from 130 to 0 over the bpm range
heart_lo = 50
heart_hi = 83
color_scaler = make_interpolater(heart_lo, heart_hi, 130, 0)

# fade settings good for on-board neopixels
animation_steps = 60
brightest = 255
dimmest = 120
fader_scaler = make_interpolater(0, 255, 0, 1)

# scaler for the pulsing, bpm to seconds
beat_scaler = make_interpolater(50, 90, 5, 0.0001)

### -- get bluetooth running --- ###

# PyLint can't find BLERadio for some reason so special case it here.
ble = adafruit_ble.BLERadio()    # pylint: disable=no-member

# start at 50
bpm = 50
bpm_raw = 50
bpm_list = [50,50,50]

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

    fill_color( 255, color_scaler(50), 0, fader_scaler(50), 0.4)

    if hr_connection and hr_connection.connected:
        print("Fetch connection")
        if DeviceInfoService in hr_connection:
            dis = hr_connection[DeviceInfoService]
            # print("Device information:", dump(dis))

            try:
                serial_number = dis.serial_number
            except:
                serial_number = "No serial number found."
            try:
                manufacturer = dis.manufacturer
            except AttributeError:
                manufacturer = "(Manufacturer Not specified)"
            try:
                model_number = dis.model_number
            except AttributeError:
                model_number = "(Model number not specified)"
            print("Device:", manufacturer, model_number, serial_number)
        else:
            print("No device information")
        hr_service = hr_connection[HeartRateService]
        print("Location:", hr_service.location)

        # bail if the serial number doesn't match my device
        if serial_number != my_serial_number:
            print("Serial number found doesn't match my device. Skipping.")
            continue

        # contiue if connected to MY heart-rate monitor:
        while hr_connection.connected:
            values = hr_service.measurement_values
            # print(values)  # returns the full heart_rate data set
            if values:
                bpm_raw = (values.heart_rate)
                if values.heart_rate == 0:
                    fill_color( 255, color_scaler(50), 0, fader_scaler(illumination), overall_brightness)
                    pixels.show()
                    print("-")
                else:
                    time.sleep(0.1)

            if bpm_raw != 0: # prevent from divide by zero

                # to smooth the bpm, average the last three readings
                # by keeping a list three elements long
                bpm_list.append(bpm_raw)
                bpm_list = bpm_list[-3:]
                bpm = sum(bpm_list) / 3

                print("bpm:", bpm_raw, "moving avg:", bpm, "bpm_list", bpm_list)

                # lauch fireworks instead of pulse if over threshold
                # but only for the actual time it's above ... so using bpm_raw
                if bpm_raw > fireworks_threshold:
                    fireworks()
                    continue

                #find interval time based on beat rate
                period = beat_scaler(bpm)

                # Fade up and down in a given period
                overall_brightness = 1  # placeholder in case we want to include this

                animation_step_length = period / animation_steps / 2 # half up, half down
                brightness_difference_per_period = int( (brightest - dimmest) / (animation_steps) )

                for illumination in range( brightest, dimmest, -brightness_difference_per_period):
                    # neopixels on board

                    fill_color( 255, color_scaler(bpm), 0, fader_scaler(illumination), overall_brightness)
                    pixels.show()
                    time.sleep(animation_step_length)

                for illumination in range( dimmest, brightest, brightness_difference_per_period):
                    # neopixels on board

                    fill_color( 255, color_scaler(bpm), 0, fader_scaler(illumination), overall_brightness)
                    pixels.show()
                    time.sleep(animation_step_length * 0.2) # get brighter faster





