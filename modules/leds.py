# leds.py
import time
from rpi_ws281x import PixelStrip, Color  # type: ignore

# Configuração da fita de LEDs
LED_COUNT = 34
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 64
LED_INVERT = False

SEGMENT_MAP = {
    1: [0, 1, 2],
    2: [3, 4, 5],
    3: [6, 7, 8],
    4: [9, 10],
    5: [12, 13],
    6: [14, 15, 16],
    7: [17, 18],
    8: [20, 21],
    9: [23, 24],
    10: [25, 26, 27],
    11: [28, 29, 30],
    12: [31, 32, 33]
}

OFF    = Color(0, 0, 0)
PURPLE = Color(160, 32, 240)
RED    = Color(255, 0, 0)
GREEN  = Color(0, 255, 0)
BLUE   = Color(0, 0, 255)
WHITE  = Color(255, 255, 255)
YELLOW = Color(255, 255, 0)

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

def activate_segment(position: int, color: Color):
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position} (deve ser 1-12)")
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, color)
    strip.show()

def deactivate_segment(position: int):
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position}")
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, OFF)
    strip.show()

def blink_segment(position: int, color: Color, duration: float = 1.5, blinks: int = 3):
    for _ in range(blinks):
        activate_segment(position, color)
        time.sleep(duration/(2*blinks))
        deactivate_segment(position)
        time.sleep(duration/(2*blinks))

def blink_led(position: int, color: Color = YELLOW, duration: float = 1.5, blinks: int = 3):
    blink_segment(position, color, duration, blinks)

def indicateRightPos(pos):
    activate_segment(pos, BLUE)

def warnOccupiedPos(pos):
    blink_segment(pos, RED, duration=3, blinks=5)

def warnWrongPos(right_pos, wrong_pos):
    for _ in range(3):
        activate_segment(right_pos, WHITE)
        activate_segment(wrong_pos, RED)
        time.sleep(0.25)
        deactivate_segment(right_pos)
        deactivate_segment(wrong_pos)
        time.sleep(0.25)

def rightPos(pos):
    activate_segment(pos, GREEN)
    time.sleep(1.5)
    deactivate_segment(pos)

def ledsOff():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, OFF)
    strip.show()

def startUp():
    print("Testando LEDs...")
    for pos in SEGMENT_MAP:
        activate_segment(pos, PURPLE)
        time.sleep(0.2)
        deactivate_segment(pos)
    ledsOff()
