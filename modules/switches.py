#Switches controll module

# Libraries import
import RPi.GPIO as GPIO                                             # type: ignore
import time
import os 

# Defines GPIO pins to be used
#               1  2  3   4   5   6   7  8   9  10 11 12
switchesPins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13]

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
def compareSwitches(old):
    switchNum = 0
    switchNumList = []
    for switch in old:
        if GPIO.input(switch) != old[switchNum]:
           switchNumList.append(switchNum)         
        switchNum += 1
    return switchNumList

# Function to return a boolean if the switches stayed with the same status
def didntChange(states):
    if states.lenght == 0:
        return True
    else:
        return False