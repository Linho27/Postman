#Fan controlling module

# Libraries import
import RPi.GPIO as GPIO                     # type: ignore
from gpiozero import CPUTemperature         # type: ignore
from time import sleep

# Pin & MaxTemp definition
fanPin = 17
tempLimitMax = 40

# Global fanStatus variable for tracking the fan state
fanStatus = False  # Start fan status as off

# Check temperature functions
def check_temp():
    # Pins setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fanPin, GPIO.OUT)
    GPIO.output(fanPin, GPIO.LOW)
    global fanStatus  # Declare fanStatus as global so it can be modified here
    cpu = CPUTemperature()  # Creating instance to read CPU temp
    
    while True:
        cpuTemp = cpu.temperature  # Get CPU temp
        print(f"Temperatura atual: {cpuTemp}°C")  # Print said temp for Debug purposes
        
        # If the CPU temperature is higher than the limit and the fan is off, turn it on
        if cpuTemp > tempLimitMax and not fanStatus:
            print("Temperatura alta! Ligando ventoinha...")
            GPIO.output(fanPin, GPIO.HIGH)
            fanStatus = True  # Update fanStatus to True when the fan is turned on
            
        # If the CPU temperature is lower than the limit and the fan is on, turn it off
        elif cpuTemp <= tempLimitMax and fanStatus:
            print("Temperatura dentro do limite. Desligando ventoinha...")
            GPIO.output(fanPin, GPIO.LOW)
            fanStatus = False  # Update fanStatus to False when the fan is turned off
        
        sleep(5)  # Wait for 5 seconds to prevent overloading the Raspberry Pi