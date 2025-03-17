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
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff()