from modules.fan import *
from modules.leds import *
from modules.switches import *
import RPi.GPIO as GPIO
import threading

if __name__ == "__main__":
        try:
            #Start fan controll in a thread
            tempThread = threading.Thread(target=check_temp) # type: ignore
            tempThread.start()
            tempThread.join()
            indicateRightPos(1) # type: ignore
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff() # type: ignore