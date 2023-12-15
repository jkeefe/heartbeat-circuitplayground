import time
import board
import neopixel

#NeoPixel code
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.4, auto_write=False)
RED = (255, 0, 0)
LIGHTRED = (25, 0, 0)
BLANK = (0,0,0)

def color_chase(color, wait):
    for i in range(10):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
    time.sleep(1)

def fill_color(color):
    for i in range(10):
        pixels[i] = color
    pixels.show()

def make_interpolater(left_min, left_max, right_min, right_max): 
    # Figure out how 'wide' each range is  
    leftSpan = left_max - left_min  
    rightSpan = right_max - right_min  

    # Compute the scale factor between left and right values 
    scaleFactor = float(rightSpan) / float(leftSpan) 

    # create interpolation function using pre-calculated scaleFactor
    def interp_fn(value):
        return right_min + (value-left_min)*scaleFactor

    return interp_fn

    ## usage: 
    ## scaler = make_interpolater(0, 10, 100, 200)
    ## x = scaler(50)
    ## ... can make many in each project!


# # animation to show initialization of program
# color_chase(LIGHTRED, 0.1)  # Increase the number to slow down the color chase

# make color range
# 50 bpm = 255,130,0 
# 85 bpm = 255,0,0 (full red)
# ... so scale the green from 130 to 0 over the bpm range
heart_lo = 50
heart_hi = 83
color_scaler = make_interpolater(heart_lo, heart_hi, 130, 0)

while True:
    bpm = 50
    fill_color( (255, color_scaler(bpm), 0))
    time.sleep(1)

    bpm = 60
    fill_color( (255, color_scaler(bpm), 0))
    time.sleep(1)

    bpm = 70
    fill_color( (255, color_scaler(bpm), 0))
    time.sleep(1)

    bpm = 80
    fill_color( (255, color_scaler(bpm), 0))
    time.sleep(1)

    bpm = 85
    fill_color( (255, color_scaler(bpm), 0))
    time.sleep(1)

