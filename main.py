from modules.fan import *
import RPi.GPIO as GPIO
import threading

if __name__ == "__main__":
        try:
            #Start fan controll in a thread
            tempThread = threading.Thread(target=check_temp)
            tempThread.start()
            tempThread.join()
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()