from modules.fan import *
import RPi.GPIO as GPIO

if __name__ == "__main__":
        try:
            check_temp()
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()