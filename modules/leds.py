#LEDs controlling module

# Libraries import
import time
from rpi_ws281x import PixelStrip, Color

# Parameters configuration
LED_COUNT = 36        
LED_PIN = 18          
LED_FREQ_HZ = 800000 
LED_DMA = 10          
LED_BRIGHTNESS = 128  # 0-255
LED_INVERT = False

# LED strip configuration
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# Function to define every LED on strip
def color_wipe(strip, color, wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

# Light every LED on strip to Purple(160, 32, 240)
def startUp():
    print("Testing LEDs.")
    color_wipe(strip, Color(160, 32, 240))

# Turn off every LED on strip
def ledsOff():
    print("Turning off LEDs.")
    color_wipe(strip, Color(0, 0, 0), wait_ms=10)  # Turns off LEDs

def indicateRightPos(pos):
    sleep(1)

def warnWrongPos(rightPos, wrongPos):
    sleep(1)

def rightPos(rightpos):
    sleep(1)