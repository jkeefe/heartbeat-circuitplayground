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

def fill_color(red, green, blue, fade, brightness):
    for i in range(10):
        pixels[i] = (red*fade*brightness, green*fade*brightness, blue*fade*brightness)
    pixels.show()

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


# # animation to show initialization of program
# color_chase(LIGHTRED, 0.1)  # Increase the number to slow down the color chase

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

beat_scaler = make_interpolater(50, 90, 5, 0.001)

while True:

    bpm = 70

    period = beat_scaler(bpm)

    # Fade up and down in a given period

    overall_brightness = 1

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





