# ================================
# 💡 LEDs control module
# ================================

# ================================
# 📦 Imports
# ================================
import time
from rpi_ws281x import PixelStrip, Color  # type: ignore

# ================================
# 🎞 LED strip configuration
# ================================
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

# ================================
# 🍭 Color variables
# ================================
OFF    = Color(0, 0, 0)
PURPLE = Color(160, 32, 240)
RED    = Color(255, 0, 0)
GREEN  = Color(0, 255, 0)
BLUE   = Color(0, 0, 255)
WHITE  = Color(255, 255, 255)
YELLOW = Color(255, 255, 0)

# ================================
# 🎞 LED strip initialization
# ================================
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# ================================
# ⚙ Startup function
# ================================
def startUpLEDS():
    print("Testando LEDs...")
    for pos in SEGMENT_MAP:
        activate_segment(pos, PURPLE)
        strip.show() # Adicionado para atualizar o LED imediatamente
        time.sleep(0.2)
        deactivate_segment(pos)
        strip.show() # Adicionado para desligar o LED imediatamente
        time.sleep(0.2)
    ledsOff()

# ================================
# ⚙ Crude functions
# ================================

def blink_segment(position: int, color: Color, duration: float = 1.5, blinks: int = 3):
    for _ in range(blinks):
        activate_segment(position, color)
        strip.show() # Adicionado para atualizar o LED imediatamente
        time.sleep(duration/(2*blinks))
        deactivate_segment(position)
        strip.show() # Adicionado para desligar o LED imediatamente
        time.sleep(duration/(2*blinks))

def blink_multiple_segments(positions: list[int], color: Color, duration: float = 1.5, blinks: int = 3):
    """Faz múltiplos segmentos piscarem simultaneamente."""
    for _ in range(blinks):
        for pos in positions:
            if pos in SEGMENT_MAP:
                # setPixelColor é chamado diretamente, pois activate_segment não faz strip.show()
                for led_index in SEGMENT_MAP[pos]:
                    strip.setPixelColor(led_index, color)
        strip.show() # Atualiza a fita uma única vez após ativar todos
        time.sleep(duration / (2 * blinks))
        for pos in positions:
            if pos in SEGMENT_MAP:
                # setPixelColor é chamado diretamente, pois deactivate_segment não faz strip.show()
                for led_index in SEGMENT_MAP[pos]:
                    strip.setPixelColor(led_index, OFF)
        strip.show() # Atualiza a fita uma única vez após desativar todos
        time.sleep(duration / (2 * blinks))


def activate_segment(position: int, color: Color):
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position} (deve ser 1-12)")
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, color)
    # strip.show() # Removido daqui para ser controlado externamente ou por blink_multiple_segments

def deactivate_segment(position: int):
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position}")
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, OFF)
    # strip.show() # Removido daqui para ser controlado externamente ou por blink_multiple_segments

def ledsOff():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, OFF)
    strip.show()

# ================================
# ▶ Functions
# ================================

def indicateRightPos(pos):
    activate_segment(pos, BLUE)
    strip.show() # Adicionado para garantir atualização imediata

def warnOccupiedPos(pos):
    # Esta função não será mais chamada diretamente pelo monitor para múltiplas posições
    # Mantenho para caso seja usada noutras partes do código
    blink_segment(pos, RED, duration=3, blinks=5)

def warnWrongPos(right_pos, wrong_pos):
    for _ in range(3):
        activate_segment(right_pos, WHITE)
        activate_segment(wrong_pos, RED)
        strip.show() # Atualiza ambos os segmentos ao mesmo tempo
        time.sleep(0.25)
        deactivate_segment(right_pos)
        deactivate_segment(wrong_pos)
        strip.show() # Desativa ambos os segmentos ao mesmo tempo
        time.sleep(0.25)

    deactivate_segment(right_pos)
    deactivate_segment(wrong_pos)
    strip.show() # Garante que ficam todos desligados no final

def rightPos(pos):
    activate_segment(pos, GREEN)
    strip.show() # Adicionado para garantir atualização imediata
    time.sleep(3)
    deactivate_segment(pos)
    strip.show() # Adicionado para garantir que desliga imediatamente