import board
import neopixel

LED_COUNT = 60  # Altere para o número de LEDs da sua fita

pixels = neopixel.NeoPixel(board.D18, LED_COUNT, auto_write=True)
pixels.fill((255, 255, 255))
