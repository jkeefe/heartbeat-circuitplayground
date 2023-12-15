# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials: PWM with Fixed Frequency example."""
import time
import board
import pwmio

# LED setup for most CircuitPython boards:
led = pwmio.PWMOut(board.AUDIO)
# LED setup for QT Py M0:
# led = pwmio.PWMOut(board.SCK, frequency=5000, duty_cycle=0)

while True:
    for i in range(100):
        # PWM LED up and down
        if i < 50:
            led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
        else:
            led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
        print(led.duty_cycle)
        time.sleep(0.01)


# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries

# SPDX-License-Identifier: MIT

# """CircuitPython Essentials PWM pin identifying script"""
# import board
# import pwmio

# for pin_name in dir(board):
#     pin = getattr(board, pin_name)
#     try:
#         p = pwmio.PWMOut(pin)
#         p.deinit()
#         print("PWM on:", pin_name)  # Prints the valid, PWM-capable pins!
#     except ValueError:  # This is the error returned when the pin is invalid.
#         print("No PWM on:", pin_name)  # Prints the invalid pins.
#     except RuntimeError:  # Timer conflict error.
#         print("Timers in use:", pin_name)  # Prints the timer conflict pins.
#     except TypeError:  # Error returned when checking a non-pin object in dir(board).
#         pass  # Passes over non-pin objects in dir(board).
