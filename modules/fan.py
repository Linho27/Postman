#Fan controlling module

#Libraries import
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
from time import sleep

#Pin & MaxTemp definition
fanPin = 17
tempLimit= 40

#Pins setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(fanPin, GPIO.OUT)

#Check temperature function
def check_temp():
    fanStatus = False #Start fan status as off
    cpu = CPUTemperature() #Creating instance to read cpu temp
    while True:
        cpuTemp = cpu.temperature   #Get cpu temp
        print(f"Temperatura atual: {cpuTemp}°C")    #Print said temp for Debug purposes
        if cpuTemp > tempLimit and fanStatus == False:  #If cpu temp is higher then the limit & fan is not on, enable it
            print("Temperatura alta! Ligando ventoinha...")
            GPIO.output(fanPin, GPIO.HIGH)
            fanStatus = True
        elif fanStatus == True:
            print("Temperatura dentro do limite. Desligando ventoinha...")  #If cpu temp is lower then the limit & fan is  on, disable it
            GPIO.output(fanPin, GPIO.LOW)
            fanStatus = False
        sleep(5)    #5 second delay to not stress the raspberry
