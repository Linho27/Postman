import time
import board
import neopixel

# Quantos LEDs tens na fita?
NUM_LEDS = 34

# Define o pino de dados (normalmente D18 → GPIO18 → board.D18)
PIN = board.D18

# Inicializa os LEDs
pixels = neopixel.NeoPixel(PIN, NUM_LEDS, brightness=0.5, auto_write=False)

# Função de teste: vermelho, verde, azul
def test_leds():
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # R, G, B
    for color in colors:
        pixels.fill(color)
        pixels.show()
        print(f"LEDs acesos com cor: {color}")
        time.sleep(1)

    # Desliga todos no fim
    pixels.fill((0, 0, 0))
    pixels.show()
    print("LEDs desligados.")

if __name__ == "__main__":
    test_leds()
