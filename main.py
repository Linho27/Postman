from modules.fan import *
from modules.leds import *
from modules.switches import *
from modules.qrreader import *
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
                
           # Scan for QR codes until one is read
                qr_code = None
                while qr_code is None:
                    qr_code = scan_qr_code()

                # Look for ID in QR code with MTS
                platePosition = get_id_from_qr(qr_code, mts)

                # If position is occupied
                if is_position_occupied(platePosition):
                    warnOccupiedPos(platePosition)
                else:
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
                    else:
                        # Handle the case where the position is not correct
                        warnWrongPos(platePosition, switchesStatesNew)
                        
        except KeyboardInterrupt:
            print("Programa interrompido pelo usuário.")
        finally:
            GPIO.cleanup()
            ledsOff()