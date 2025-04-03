# LEDs controlling module with right-side activation

# Libraries import
import time
from rpi_ws281x import PixelStrip, Color  # type: ignore

# LED strip configuration
LED_COUNT = 36        # Total de LEDs
LED_PIN = 18          # GPIO 18 (PWM0)
LED_FREQ_HZ = 800000  # 800kHz
LED_DMA = 10          
LED_BRIGHTNESS = 64   # 0-255
LED_INVERT = False    

# Segmentação ajustada (LEDs à direita por posição)
SEGMENT_MAP = {
    1: [0, 1, 2],     # LEDs 1-3 (esquerda para direita)
    2: [3, 4, 5],     # LEDs 4-6
    3: [6, 7, 8],     # LEDs 7-9
    4: [9, 10],       # LEDs 10-11  
    5: [12, 13],      # LEDs 13-14 (12 não usado)
    6: [14, 15, 16],          # LED 16 (índice 15)
    7: [17, 18],      # LEDs 18-19 (índices 17-18)
    8: [20, 21],      # LEDs 21-22 (índices 20-21)
    9: [23, 24],      # LEDs 24-25 (índices 23-24)
    10: [25, 26, 27], # LEDs 26-28 (índices 25-27)
    11: [28, 29, 30], # LEDs 29-31 (índices 28-30)
    12: [31, 32, 33]  # LEDs 32-34 (índices 31-33)
}

# Cores pré-definidas
OFF = Color(0, 0, 0)
PURPLE = Color(160, 32, 240)
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)

# Inicialização da fita LED
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

def activate_segment(position: int, color: Color):
    """Ativa os LEDs à direita da posição especificada"""
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position} (deve ser 1-12)")
    
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, color)
    strip.show()

def deactivate_segment(position: int):
    """Desativa os LEDs da posição especificada"""
    if position not in SEGMENT_MAP:
        raise ValueError(f"Posição inválida: {position}")
    
    for led_index in SEGMENT_MAP[position]:
        strip.setPixelColor(led_index, OFF)
    strip.show()

def blink_segment(position: int, color: Color, duration: float = 1.5, blinks: int = 3):
    """Pisca os LEDs da posição especificada"""
    for _ in range(blinks):
        activate_segment(position, color)
        time.sleep(duration/(2*blinks))
        deactivate_segment(position)
        time.sleep(duration/(2*blinks))

# Funções principais (interface compatível)
def indicateRightPos(pos):
    """Indica posição correta com LED azul"""
    activate_segment(pos, BLUE)

def warnOccupiedPos(pos):
    """Alerta posição ocupada com LED vermelho piscante"""
    blink_segment(pos, RED, duration=15, blinks=10)

def warnWrongPos(right_pos, wrong_pos):
    """Indica posição errada e correta"""
    for _ in range(6):  # 3 piscadas
        activate_segment(right_pos, GREEN)
        activate_segment(wrong_pos, RED)
        time.sleep(0.25)
        deactivate_segment(right_pos)
        deactivate_segment(wrong_pos)
        time.sleep(0.25)

def rightPos(pos):
    """Confirma posição correta com LED verde"""
    activate_segment(pos, GREEN)
    time.sleep(10)
    deactivate_segment(pos)

def ledsOff():
    """Desliga todos os LEDs"""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, OFF)
    strip.show()

def startUp():
    """Teste inicial de LEDs"""
    print("Testando LEDs...")
    for pos in SEGMENT_MAP:
        activate_segment(pos, PURPLE)
        time.sleep(0.2)
        deactivate_segment(pos)
    ledsOff()