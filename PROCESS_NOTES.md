# Process Notes

## Circuit Playground

### New boards

- Double-click the reset button while connected to a laptop using a data-good cord
- Look in INFO_UF2.txt
- If it looks like this, it's too old:

```
UF2 Bootloader 0.2.11-8-g2c13fd5-dirty lib/nrfx (v1.1.0-1-g096e770) lib/tinyusb (legacy-755-g55874813) s140 6.1.1
Model: Adafruit Circuit Playground nRF52840
Board-ID: nRF52840-CircuitPlayground-revD
Date: Jul 13 2019
```

Because: 

```
CircuitPython 8.2.0 and later require UF2 bootloader version 0.6.1 or later. Older bootloaders cannot load the firmware. To check the version of your board's bootloader, look at INFO_UF2.TXT 
```

So ...

- Go get the update bootloader file on [this github page](https://github.com/adafruit/Adafruit_nRF52_Bootloader/releases/tag/0.7.0)
- Look for the file that begins with `circuitplayground_` and ends with `.zip` like:  `circuitplayground_nrf52840_bootloader-0.8.0_s140_6.1.1.zip`
- Click to download
- Follow the [command-line instructions](https://learn.adafruit.com/introducing-the-adafruit-nrf52840-feather/update-bootloader-use-command-line). Note that the `-macos`` part of the comands are no longer used.
- (I've already installed adafruit-nfutil)
- in terminal, type `ls /dev/cu.*`
    - Look for something like `/dev/cu.usbmodem14201`
- cd into the Downloads folder, where the update is
- double-click the reset button if all the lights aren't green, in boot mode
- do this command, replacing the usbmodem part and the name of the zipfile:

```
./adafruit-nrfutil --verbose dfu serial --package circuitplayground_nrf52840_bootloader-0.8.0_s140_6.1.1.zip -p /dev/cu.usbmodem14201 -b 115200 --singlebank --touch 1200
```

- looking again at INFO_UF2.txt, should look like this:

```
UF2 Bootloader 0.8.0 lib/nrfx (v2.0.0) lib/tinyusb (0.12.0-145-g9775e7691) lib/uf2 (remotes/origin/configupdate-9-gadbb8c7)
Model: Adafruit Circuit Playground nRF52840
Board-ID: nRF52840-CircuitPlayground-revD
Date: Sep 29 2023
SoftDevice: S140 6.1.1
```

- Now follow the [Circit Python install instructions](https://learn.adafruit.com/ble-heart-rate-display-pendant/circuitpython) for Bluefruit:
    - Find the latest Circuit Python [on this page](https://circuitpython.org/board/circuitplayground_bluefruit/)
    - Download it
    - Double-click reset
    - Drag that file ^^ to the `CIRCUITPY` drive

- rename `code.py` to `main.py` because it'll stop linting errors and also works

Done!


[Troubleshooting page](https://learn.adafruit.com/adafruit-circuit-playground-express/troubleshooting)

## Serial Monitor in VSCode(!)

Search [serial monitor](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-serial-monitor) in extensions.

## BLE monitor

Check out this [IOS app](https://apps.apple.com/us/app/nrf-connect-for-mobile/id1054362403).

## Tripod for Circuit Playground Enclosure

[Adafruit](https://www.adafruit.com/product/2629)

## Board module

Libraries: https://learn.adafruit.com/welcome-to-circuitpython/circuitpython-libraries


```
>>> import board
>>> dir(board)
['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 
 'ACCELEROMETER_INTERRUPT', 'ACCELEROMETER_SCL', 
 'ACCELEROMETER_SDA', 'BUTTON_A', 'BUTTON_B', 'D0', 'D1', 
 'D10', 'D12', 'D13', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 
 'D8', 'D9', 'I2C', 'IR_PROXIMITY', 'IR_RX', 'IR_TX', 'LIGHT', 
 'MICROPHONE_CLOCK', 'MICROPHONE_DATA', 'MISO', 'MOSI', 
 'NEOPIXEL', 'REMOTEIN', 'REMOTEOUT', 'RX', 'SCK', 'SCL', 
 'SDA', 'SLIDE_SWITCH', 'SPEAKER', 'SPEAKER_ENABLE', 'SPI', 
 'TEMPERATURE', 'TX', 'UART']
>>> 
```

PWM: https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-pwm



## Making scale interpreters for the colors

I wanted to map one range (the range of heartbeats) to a bunch of other ranges (the chenge in, say, blue colors).

This [stackoverflow answer](https://stackoverflow.com/a/1970037) was really cool, because it allows me to make many different scaler functions and then use them at will:

---
This would actually be a good case for creating a closure, that is write a function that returns a function. Since you probably have many of these values, there is little value in calculating and recalculating these value spans and factors for every value, nor for that matter, in passing those min/max limits around all the time.

Instead, try this:

```python
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
```


Now you can write your processor as:

```python
# create function for doing interpolation of the desired
# ranges
scaler = make_interpolater(1, 512, 5, 10)

# receive list of raw values from sensor, assign to data_list

# now convert to scaled values using map 
scaled_data = map(scaler, data_list)

# or a list comprehension, if you prefer
scaled_data = [scaler(x) for x in data_list]
```

---

OR ... make many different ones ... like:

```python
orange_scaler = make_interpolator(0, 50, 255, 110)
```

## Accellerometer

xyz + shake + tap code: https://learn.adafruit.com/adafruit-lis3dh-triple-axis-accelerometer-breakout/python-circuitpython

```
First the range of the accelerometer is set by changing the range property on the LIS3DH object.  Notice how you can set it to one of four possible ranges, where a 2G range gives you a lot of accuracy in a small range vs. up to a 16G range with less accuracy over a much wider range.  You'll need to pick the right range for your usage needs, although starting with a simple 2G range is a smart idea.

Next in the main loop you can see the acceleration property is read.  This property is a 3-tuple with the X, Y, Z acceleration values that were read by the sensor.  Remember these values are in meters per second squared so you might need to convert to other units depending on your needs.

That's all there is to reading the accelerometer values!
```

