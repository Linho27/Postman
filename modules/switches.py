# ================================
# 🔗 Switches control module
# ================================

# ================================
# 📦 Imports
# ================================
import os
import time
import RPi.GPIO as GPIO  # type: ignore
from dotenv import load_dotenv
from typing import List, Dict
from modules.connection import *

# ================================
# 🔐 Environment Variables
# ================================
load_dotenv()
SWITCHES_PINS_RAW = os.getenv("SWITCHES_PINS")

if SWITCHES_PINS_RAW is None:
    raise ValueError("Variável de ambiente 'SWITCHES_PINS' não definida.")

# DEBUG: Mostra o valor lido da variável de ambiente
print("DEBUG SWITCHES_PINS_RAW:", repr(SWITCHES_PINS_RAW))

# Remove colchetes, aspas e espaços
SWITCHES_PINS_RAW = SWITCHES_PINS_RAW.strip().strip("[](){}'\"")

# Faz split e converte para inteiros, ignorando elementos vazios ou inválidos
SWITCHES_PINS = []
for pin in SWITCHES_PINS_RAW.split(","):
    pin = pin.strip()
    if pin.lstrip('-').isdigit():
        SWITCHES_PINS.append(int(pin))
    else:
        if pin:  # Só mostra aviso se não for string vazia
            print(f"AVISO: Ignorado valor inválido em SWITCHES_PINS: '{pin}'")

if not SWITCHES_PINS:
    raise ValueError("Nenhum pino válido foi encontrado em 'SWITCHES_PINS'.")

print("DEBUG SWITCHES_PINS (lista final):", SWITCHES_PINS)

# ================================
# ⚙️ GPIO Initialization
# ================================
_initialized = False

def _init_gpio():
    global _initialized
    if not _initialized:
        GPIO.setmode(GPIO.BCM)
        for pin in SWITCHES_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        _initialized = True

# ================================
# ▶️ Functions
# ================================

def getSwitches() -> List[int]:
    """Retorna os estados brutos de todos os switches (1=solto, 0=pressionado)."""
    _init_gpio()
    return [GPIO.input(pin) for pin in SWITCHES_PINS]

def compareSwitches(oldStates: List[int]) -> List[int]:
    """Compara estados atuais com anteriores. Retorna índices das mudanças."""
    current = getSwitches()
    return [i for i in range(len(SWITCHES_PINS)) if current[i] != oldStates[i]]

def didntChange(states: List[int]) -> bool:
    """Verifica se não houve mudanças nos estados."""
    return len(states) == 0

def update_positions() -> Dict[int, bool]:
    """
    Retorna um dicionário {posição: ocupada}
    ocupada=True se pressionado (GPIO=0)
    """
    states = getSwitches()
    return {pos+1: (state == 0) for pos, state in enumerate(states)}

def syncSwitchesWithAPI() -> Dict[int, bool]:
    """
    Sincroniza todos os switches físicos com o estado da API.
    Se houver diferença, faz o toggle na API.
    Retorna dicionário {posição: resultado_toggle}
    """
    _init_gpio()
    results = {}
    current_states = getSwitches()
    for position in range(1, len(SWITCHES_PINS)+1):
        pin = SWITCHES_PINS[position-1]
        physical_state = current_states[position-1] == 0  # 0 = pressionado
        api_state = isOccupied(position)
        if physical_state != api_state:
            result = togglePos(position)
            results[position] = result
    return results

def cleanup():
    """Limpa recursos do GPIO."""
    global _initialized
    if _initialized:
        GPIO.cleanup()
        _initialized = False
