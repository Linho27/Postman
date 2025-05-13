import board
import neopixel

# Número de LEDs na fita
LED_COUNT = 60  # Substitua pelo número real de LEDs

# Inicializa o objeto NeoPixel
pixels = neopixel.NeoPixel(board.D17, LED_COUNT, auto_write=True)

# Define todos os LEDs para branco (255, 255, 255)
pixels.fill((255, 255, 255))
