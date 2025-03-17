#LEDs controlling module

# Libraries import
import time
from rpi_ws281x import PixelStrip, Color

# Define colors for later use

OFF = Color(0, 0, 0)
PURPLE = Color(160, 32, 240)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)

# Parameters configuration
LED_COUNT = 36        
LED_PIN = 18          
LED_FREQ_HZ = 800000    #800kHz for WS2813
LED_DMA = 10          
LED_BRIGHTNESS = 128    # 0-255
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

# Light every LED on strip
def startUp():
    print("Testing LEDs.")
    color_wipe(strip, PURPLE)

# Turn off every LED on strip
def ledsOff():
    print("Turning off LEDs.")
    color_wipe(strip, Color(0, 0, 0), wait_ms=10)  # Turns off LEDs

# Turn on LEDs on right position to place the plate 
def indicateRightPos(rightIndicatorPos):
    segmentStart, segmentEnd = calcSegment(rightIndicatorPos)
    enableSegment(segmentStart, segmentEnd, BLUE)

# Turn on blinking LEDs on right and wrong plate position
def warnWrongPos(rightPos, wrongPos):
    #Blink right pos
    segmentStartR, segmentEndR = calcSegment(rightPos)
    enableIntermittentSegment(segmentStartR, segmentEndR, GREEN)
    #Blink wrong pos
    segmentStartW, segmentEndW = calcSegment(rightPos)
    enableIntermittentSegment(segmentStartW, segmentEndW, RED)
    time.sleep(1.5)
    
# Turn on LEDs on right plate position
def rightPos(rightPos):
    segmentStart, segmentEnd = calcSegment(rightPos)
    enableSegment(segmentStart, segmentEnd, GREEN)

def calcSegment(segment):
    leds_per_segment = 3  # Each segment has 3 LEDs
    segmentStart = (segment - 1) * leds_per_segment
    segmentEnd = segmentStart + leds_per_segment
    return segmentStart, segmentEnd

def enableSegment(start, end, color):
    for i in range(start, end):
        strip.setPixelColor(i, color)  # Set the LED color
    strip.show()

def enableIntermittentSegment(start, end, color):
    for i in range(start, end):                     
        if strip.getPixelColor(i) == OFF:
            strip.setPixelColor(i, color)
        else:
            strip.setPixelColor(i, OFF)
    strip.show()