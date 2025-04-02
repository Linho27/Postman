#Switches control module

# Libraries import
import RPi.GPIO as GPIO                     # type: ignore
import time
import os 
from connection import togglePos, isOccupied  # Importa funções para verificar e alternar estado na API

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
def compareSwitches(oldStates):
    switchNumList = []
    for i, pin in enumerate(switchesPins):  # Iterate over the pins correctly
        if GPIO.input(pin) != oldStates[i]:  # Compare current state with the previous one
            switchNumList.append(i)         
    return switchNumList

# Function to return a boolean if the switches remained unchanged
def didntChange(states):
    return len(states) == 0

# Function to sync switch states with API
def syncSwitchesWithAPI():
    for i, pin in enumerate(switchesPins, start=1):  # Começa do 1 para coincidir com posições
        state = GPIO.input(pin)
        ocupado = isOccupied(i)  # Verifica na API se a posição está ocupada
        if (state == GPIO.LOW and not ocupado) or (state == GPIO.HIGH and ocupado):
            togglePos(i)  # Alterna apenas se o estado for diferente
    print("Estados dos switches sincronizados com a API.")
