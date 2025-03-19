from modules.fan import *
from modules.leds import *
from modules.switches import *
import RPi.GPIO as GPIO                     # type: ignore
import multiprocessing
import time

if __name__ == "__main__":
        try:
            #Start fan controll in a thread
            tempChecking = multiprocessing.Process(target=check_temp, daemon=True)
            tempChecking.start()
            while True:
                warnWrongPos(1, 3) #Testing
                time.sleep(1)
                
            """
            while True:
                MTS connection here

                Scan for qr codes until one is read

                Look for id in qr code with mts

                If position is occupied
                    warnOccupiedPos(platePosition)
                else
                    switchesStates = getSwitches()
                    indicateRightPos()
                    while didntChange(compareSwitches(switchesStates)):
                         time.sleep(0.5)
                    ledsOff()
                    switchesStatesNew = getSwitches()
                    if len(switchesStatesNew) == 1 and switchesStatesNew[0] == platePosition:
                        rightPos(platePosition)
                        time.sleep(10)
                        ledsOff()
                    else
                        

            """
                
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff()