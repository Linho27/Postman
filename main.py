from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.connection import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time

if __name__ == "__main__":
        try:
            #Start fan controll in a thread
            tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
            tempChecking.start()
            while True:
                
                code = input()                      # Wait for bar/qr code input
                platePosition = getPos(code)        # Look for ID with code with MTS
                if code == '404':
                    break
                else:
                    if isOccupied(platePosition):       # If position is occupied
                        warnOccupiedPos(platePosition)
                    else:
                        switchesStates = getSwitches()                      #Save switches states
                        indicateRightPos(platePosition)                     #Indicate where to place the plate
                        while didntChange(compareSwitches(switchesStates)): #Wait until something changes
                            time.sleep(0.5)
                        ledsOff()                                           #Turn off indicating light
                    
                        switchesStatesNew = compareSwitches(switchesStates) #Compare old switches states to now
                        positionIsRight = False
                        while not positionIsRight:                          #Repeat while position is wrong
                            time.sleep(1)
                            switchesStatesNew = compareSwitches(switchesStates) #Compare old switches states to now
                            if switchesStatesNew[0] == platePosition:           #If position is right
                                rightPos(platePosition)                         #Turn on green leds for 10s
                                positionIsRight = True
                            else:                                               #If position is wrong
                                warnWrongPos(platePosition, switchesStatesNew[0])   #Blinking leds (right and wrong pos)

        except KeyboardInterrupt:                           #Handle ctrl+c
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff()
            print("Programa interrompido sem problemas.")