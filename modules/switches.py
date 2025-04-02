#Switches controll module

# Libraries import
import RPi.GPIO as GPIO                     # type: ignore
import time
import os 

# Defines GPIO pins to be used
#               1  2  3   4   5   6   7  8   9  10 11 12
switchesPins = [4, 5, 6, 12, 13, 16, 20, 21, 22, 23, 24, 25]

# GPIO pins configuration
GPIO.setmode(GPIO.BCM)
for pin in switchesPins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to get status of the 12 switches
def getSwitches():
    switchStates = []
    for switch in switchesPins:
        state = GPIO.input(switch)
        switchStates.append(state)
    return switchStates

# Function to compare the status of a list of switches
def compareSwitches(oldStates):
    switchNumList = []
    for i, pin in enumerate(switchesPins):  # Iterate over the pins correctly
        if GPIO.input(pin) != oldStates[i]:  # Compare current state with the previous one
            switchNumList.append(i)         
    return switchNumList

# Function to return a boolean if the switches stayed with the same status
# Function to return a boolean if the switches remained unchanged
def didntChange(states):
    if len(states) == 0:  # Corrected the typo
        return True
    else:
        return False
