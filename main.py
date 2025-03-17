from modules.fan import *
from modules.leds import *
from modules.switches import *
import RPi.GPIO as GPIO                                                     # type: ignore
import threading

if __name__ == "__main__":
        try:
            #Start fan controll in a thread
            tempThread = threading.Thread(target=check_temp)  
            tempThread.start()
            tempThread.join()
            while True:
                warnWrongPos(1, 3) #Testing
                print(1)
                
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
                    if platePosition != 
            """
                
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff()